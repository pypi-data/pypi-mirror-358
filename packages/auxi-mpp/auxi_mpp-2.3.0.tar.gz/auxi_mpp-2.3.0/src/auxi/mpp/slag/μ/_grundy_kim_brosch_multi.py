import math
from collections.abc import Callable
from typing import Any, ClassVar

from pydantic import Field
from scipy.optimize._shgo import shgo  # type: ignore

from auxi.chemistry.validation import strCompoundFormula
from auxi.core.physicalconstants import R
from auxi.core.validation import floatFraction, floatPositiveOrZero, strNotEmpty

from ..state import SilicateSlagEquilibriumTpxaState
from ._model import Model


class GrundyKimBroschMulti(
    Model[floatPositiveOrZero, floatPositiveOrZero, dict[str, floatFraction], dict[str, dict[str, floatFraction]]]
):
    """
    Multi-component silicate slag dynamic viscosity model by Grundy, Kim, and Brosch.

    Args:
        bff : Bond fraction function with temperature, pressure, composition and phase constituent activities as input and returns a dictionary of bond fractions. Eg. def my_bff(T: float, p: float, x: dict[str, float], a:dict[str, dict[str, float]]) -> dict[str, float]: ...

    Returns:
       Dynamic viscosity in [Pa.s].

    References:
        grundy2008-part1, grundy2008-part2, kim2012-part3
    """

    data: ClassVar[dict[str, dict[str, Any]]] = {}

    references: ClassVar[list[strNotEmpty]] = ["grundy2008-part1", "grundy2008-part2"]

    bff: Callable[[float, float, dict[str, float], dict[str, dict[str, float]]], dict[str, float]]
    cation: dict[str, str] = Field(default_factory=dict)
    struc_unit: dict[str, str] = Field(default_factory=dict)
    struc_ox_count: dict[str, float] = Field(default_factory=dict)
    cation_count: dict[str, int] = Field(default_factory=dict)
    parameters: dict[str, dict[str, float]] = Field(default_factory=dict)
    names: dict[str, str] = Field(default_factory=dict)
    equilibrium_stoic: dict[str, int] = Field(default_factory=dict)
    molar_mass: dict[str, float] = Field(default_factory=dict)
    structural_x: dict[str, float] = Field(default_factory=dict)
    compound_scope: list[strCompoundFormula] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

        data = GrundyKimBroschMulti.data
        self.compound_scope = ["SiO2", "Al2O3", "MgO", "CaO", "FeO", "Fe2O3"]

        self.cation: dict[str, str] = {c: data[c]["cation"] for c in self.compound_scope}
        self.cation_count: dict[str, int] = {c: data[c]["cation_count"] for c in self.compound_scope}
        self.struc_unit: dict[str, str] = {c: data[c]["struc_unit"] for c in self.compound_scope}
        self.struc_ox_count: dict[str, float] = {c: data[c]["struc_ox_count"] for c in self.compound_scope}
        self.parameters: dict[str, dict[str, float]] = {c: data[c]["parameters"] for c in self.compound_scope}
        self.names: dict[str, str] = {data[c]["struc_unit"]: c for c in self.compound_scope}
        self.equilibrium_stoic: dict[str, int] = {c: data[c]["stoic"] for c in data}
        self.molar_mass: dict[str, float] = {c: data[c]["molar_mass"] for c in data}

    def calculate(
        self,
        T: floatPositiveOrZero = 298.15,
        p: floatPositiveOrZero = 101325,
        x: dict[str, floatFraction] = {},
        a: dict[str, dict[str, float]] = {},
    ) -> float:
        """
        Calculate multi-component system viscosity.

        Args:
            T: System temperature. [K]
            p: System pressure. [Pa]
            x: Chemical composition dictionary. [mol/mol] Eg. {"SiO2":0.5, "MgO": 0.3, "FeO": 0.2}.
            a: Phase constituent activity dictionary. Eg. {"gas_ideal": {"O2": 0.21}}. Phase and constituent name depends on how the user set up the bond fraction function.

        Returns:
            Viscosity in [Pa.s].
        """
        # validate input
        state = SilicateSlagEquilibriumTpxaState(T=T, p=p, x=x, a=a)
        for c in state.x:
            if c not in self.compound_scope:
                raise ValueError(f"{c} is not a valid formula. Valid options are '{' '.join(self.compound_scope)}'.")

        # convert input composition to structural unit fractions
        x_struc_unit = self._structural_fractions(state)

        # table 1 of grundy2008-part2
        delta_G = self._delta_G(x_struc_unit)

        # eqn 18 in grundy2008-part2
        eq_constant_K = self._constant_K(state.T, delta_G)

        # eqn 9 - 11 in grundy2008-part2
        eq_x_struc_unit = self._equilib_compositions(eq_constant_K, x_struc_unit)

        # eqn 2 to 3 in grundy2008-part1
        p_SiSi = self._probability_SiSi(state, eq_x_struc_unit)

        # eqn 4 in grundy2008-part2
        A_parameter = self._calculate_A_parameter(eq_x_struc_unit, p_SiSi, state)

        # eqn 5 in grundy2008-part2
        E_parameter = self._calculate_E_parameter(eq_x_struc_unit, p_SiSi, state)

        # eqn 10 in grundy2008-part1
        mu = math.exp(float(A_parameter + E_parameter / (R * state.T)))

        self.structural_x = eq_x_struc_unit

        return mu

    def _structural_fractions(self, state: SilicateSlagEquilibriumTpxaState) -> dict[str, float]:
        x_struc_unit: dict[str, float] = {}
        for comp in state.x:
            x_struc_unit[self.struc_unit[comp]] = self.cation_count[comp] * state.x[comp]

        x_struc_unit = self._normalise_fractions(x_struc_unit)

        return x_struc_unit

    def _full_fractions(self, struc_fracs: dict[str, float]) -> dict[str, float]:
        x_full_unit: dict[str, float] = {}
        for comp, value in struc_fracs.items():
            x_full_unit[self.names[comp]] = value / self.cation_count[self.names[comp]]

        x_full_unit = self._normalise_fractions(x_full_unit)

        return x_full_unit

    def _normalise_fractions(self, dict_in: dict[str, float]) -> dict[str, float]:
        x_sum: float = sum(dict_in[comp] for comp in dict_in)
        normalised_dict: dict[str, float] = {}
        for key, value in dict_in.items():
            normalised_dict[key] = value / x_sum
        return normalised_dict

    def _count_oxygens(self, x_comps: dict[str, float]):
        n_tot_oxygen: float = 0.0
        for comp, value in x_comps.items():
            n_tot_oxygen += self.struc_ox_count[self.names[comp]] * value
        return n_tot_oxygen

    # eqn 2 to 3 grundy2008-part1
    def _probability_SiSi(self, state: SilicateSlagEquilibriumTpxaState, x_comps: dict[str, float]) -> float:
        if x_comps["SiO2"] != 0.0:
            adjusted_comp = self._full_fractions(x_comps)
            x_b = self.bff(state.T, state.p, adjusted_comp, state.a)
            p_SiSi: float = (x_b["Si-Si"] * self._count_oxygens(x_comps)) / (2 * x_comps["SiO2"])
        else:
            p_SiSi = 0.0
        return p_SiSi

    def _calculate_A_parameter(
        self, x_comp: dict[str, float], p_SiSi: float, state: SilicateSlagEquilibriumTpxaState
    ) -> float:
        MOx = state.compounds.copy()
        MOx.remove("SiO2")
        for c in range(len(MOx)):
            MOx[c] = self.struc_unit[MOx[c]]

        # eqn 4 in grundy2008-part2
        A_SiO2_star = self.parameters["SiO2"]["A_*"]
        A_SiO2_E = self.parameters["SiO2"]["A_E"]

        # term 1
        sum_A_X = sum([self.parameters[self.names[comp]]["A"] * x_comp[comp] for comp in MOx])

        # term 4
        sum_A_MSi_X = sum([self.parameters[self.names[comp]]["A_M_Si"] * x_comp[comp] for comp in MOx])

        # term 5
        sum_XM = sum([x_comp[comp] for comp in MOx])
        if sum_XM != 0.0:
            sum_A_R_XX = sum([self.parameters[self.names[comp]]["A_M_Si_R"] * x_comp[comp] / sum_XM for comp in MOx])
        else:
            sum_A_R_XX = 0.0

        A_param = sum_A_X + x_comp["SiO2"] * (
            A_SiO2_star + A_SiO2_E * p_SiSi**40 + sum_A_MSi_X + sum_A_R_XX * (p_SiSi**4 - p_SiSi**40)
        )
        return A_param

    def _calculate_E_parameter(
        self, x_comp: dict[str, float], p_SiSi: float, state: SilicateSlagEquilibriumTpxaState
    ) -> float:
        MOx = state.compounds.copy()
        MOx.remove("SiO2")
        for c in range(len(MOx)):
            MOx[c] = self.struc_unit[MOx[c]]

        # eqn 5 in grundy2008-part2
        E_SiO2_star = self.parameters["SiO2"]["E_*"]
        E_SiO2_E = self.parameters["SiO2"]["E_E"]

        # term 1
        sum_E_X = sum([self.parameters[self.names[comp]]["E"] * x_comp[comp] for comp in MOx])

        # term 4
        sum_E_MSi_X = sum([self.parameters[self.names[comp]]["E_M_Si"] * x_comp[comp] for comp in MOx])

        # term 5
        sum_XM = sum([x_comp[comp] for comp in MOx])
        if sum_XM != 0.0:
            sum_E_R_XX = sum([self.parameters[self.names[comp]]["E_M_Si_R"] * x_comp[comp] / sum_XM for comp in MOx])
        else:
            sum_E_R_XX = 0.0

        E_param = sum_E_X + x_comp["SiO2"] * (
            E_SiO2_star + E_SiO2_E * p_SiSi**40 + sum_E_MSi_X + sum_E_R_XX * (p_SiSi**4 - p_SiSi**40)
        )
        return E_param

    def _delta_G(self, x_comp: dict[str, float]) -> dict[str, float]:
        x_SiO2 = x_comp["SiO2"]

        delta_G_CaAl2O4: float = 5000 - 100000 * x_SiO2
        delta_G_MgAl2O4: float = 13000 - 105000 * x_SiO2
        delta_G_FeAl2O4: float = -66944 * x_SiO2

        # Fe2O3 based associate species
        delta_G_CaFe2O4: float = 2092 - 5335 * x_SiO2
        return {
            "CaAl2O4": delta_G_CaAl2O4,
            "MgAl2O4": delta_G_MgAl2O4,
            "FeAl2O4": delta_G_FeAl2O4,
            "CaFe2O4": delta_G_CaFe2O4,
        }

        # eqn 18 in grundy2008-part2

    def _constant_K(self, temp: float, delta_G: dict[str, float]) -> dict[str, float]:
        const_K: dict[str, float] = {}
        for dG, value in delta_G.items():
            const_K[dG] = math.exp(value / (-1 * R * temp))
        return const_K

        # eqn 9 - 11 in grundy2008-part2

    def _equilib_compositions(self, const_K: dict[str, float], x_comp: dict[str, float]):
        # execute the solve functions only if an associate species can form
        if self._associate_species_will_form(x_comp):
            # prepare parameters
            parameters, system_lists = self._prepare_params_for_optimisation(x_comp)

            # find solutions
            solutions = self._find_solutions(parameters, system_lists, const_K, x_comp)

            # calculate adjusted composition
            new_comp = self._calc_x_star(parameters, system_lists, solutions, x_comp)

            return new_comp
        else:
            return x_comp

    def _prepare_params_for_optimisation(self, x_comp: dict[str, float]):
        # list of non-SiO2 species that can react to form associate species
        non_sio2 = ["AlO15", "CaO", "MgO", "FeO", "FeO15"]

        # associates that can form from comps in list non_sio2
        associates = ["CaAl2O4", "MgAl2O4", "FeAl2O4", "CaFe2O4"]

        # add missing components to x_comp but with amount as 0.0
        missing_comps: list[str] = []
        for comp in non_sio2:
            if comp not in x_comp:
                x_comp[comp] = 0.0
                missing_comps.append(comp)
            else:
                continue

        # get stoiciometric coefficients of compounds
        c1 = self.equilibrium_stoic[self.names[non_sio2[0]]]  # AlO15
        c2 = self.equilibrium_stoic[self.names[non_sio2[1]]]  # CaO
        c3 = self.equilibrium_stoic[self.names[non_sio2[2]]]  # MgO
        c4 = self.equilibrium_stoic[self.names[non_sio2[3]]]  # FeO
        c5 = self.equilibrium_stoic[self.names[non_sio2[4]]]  # FeO15

        # get stoiciometric coefficients of Al2O3 based associates
        a1 = self.equilibrium_stoic[associates[0]]  # CaAl2O4
        a2 = self.equilibrium_stoic[associates[1]]  # MgAl2O4
        a3 = self.equilibrium_stoic[associates[2]]  # FeAl2O4

        # get stoiciometric coefficients of Fe2O3 based associates
        a4 = self.equilibrium_stoic[associates[3]]  # CaFe2O4

        # divide all coefficients by greatest common divisor. Note, order is important
        c1, c2, c3, c4, c5, a1, a2, a3, a4 = self._gcd_a_b_c([c1, c2, c3, c4, c5, a1, a2, a3, a4])

        # get input amounts of the non-SiO2 compounds
        C1 = x_comp[non_sio2[0]]  # AlO15
        C2 = x_comp[non_sio2[1]]  # CaO
        C3 = x_comp[non_sio2[2]]  # MgO
        C4 = x_comp[non_sio2[3]]  # FeO
        C5 = x_comp[non_sio2[4]]  # FeO15

        params = (c1, c2, c3, c4, c5, a1, a2, a3, a4, C1, C2, C3, C4, C5)
        lists = (non_sio2, missing_comps, associates)

        return params, lists

    def _find_solutions(
        self,
        params: tuple[float, float, float, float, float, float, float, float, float, float, float, float, float, float],
        lists: tuple[list[Any], list[Any], list[Any]],
        const_K: dict[str, float],
        x_comp: dict[str, float],
    ):
        c1, c2, c3, c4, c5, a1, a2, a3, a4, C1, C2, C3, C4, C5 = params
        _, _, associates = lists

        # build equation to solve
        def equation_shgo(x_: Any, *args: Any):
            c1, c2, c3, c4, c5, a1, a2, a3, a4, C1, C2, C3, C4, C5, x_SiO2, const_K = args

            # equilibrium constant for every associate reaction
            const_K_1 = const_K[associates[0]]  # CaAl2O4
            const_K_2 = const_K[associates[1]]  # MgAl2O4
            const_K_3 = const_K[associates[2]]  # FeAl2O4
            const_K_4 = const_K[associates[3]]  # CaFe2O4

            # mole amounts at equilibrium -- x_[#] needs to be solved
            n_AlO15 = C1 - c1 * x_[0] - c1 * x_[1] - c1 * x_[2]
            n_CaO = C2 - c2 * x_[0] - c2 * x_[3]
            n_MgO = C3 - c3 * x_[1]
            n_FeO = C4 - c4 * x_[2]
            n_FeO15 = C5 - c5 * x_[3]

            n_CaAl2O4 = a1 * x_[0]
            n_MgAl2O4 = a2 * x_[1]
            n_FeAl2O4 = a3 * x_[2]
            n_CaFe2O4 = a4 * x_[3]

            n_SiO2 = x_SiO2

            # combined amount of moles at equilibrium
            N_tot = n_AlO15 + n_CaO + n_MgO + n_FeO + n_FeO15 + n_CaAl2O4 + n_MgAl2O4 + n_FeAl2O4 + n_CaFe2O4 + n_SiO2

            # CaAl2O4
            r1 = (n_CaAl2O4 / N_tot) ** a1 - const_K_1 * ((n_AlO15 / N_tot) ** c1 * (n_CaO / N_tot) ** c2)

            # MgAl2O4
            r2 = (n_MgAl2O4 / N_tot) ** a2 - const_K_2 * ((n_AlO15 / N_tot) ** c1 * (n_MgO / N_tot) ** c3)

            # FeAl2O4
            r3 = (n_FeAl2O4 / N_tot) ** a3 - const_K_3 * ((n_AlO15 / N_tot) ** c1 * (n_FeO / N_tot) ** c4)

            # CaFe2O4
            r4 = (n_CaFe2O4 / N_tot) ** a4 - const_K_4 * ((n_FeO15 / N_tot) ** c5 * (n_CaO / N_tot) ** c2)

            # take square to avoid negatives
            return r1**2 + r2**2 + r3**2 + r4**2

        # solve x

        # set upper bounds to input fraction divided by its stoiciometric coefficient
        bounds_x0 = (0.0, min(C1 / c1, C2 / c2))
        bounds_x1 = (0.0, min(C1 / c1, C3 / c3))
        bounds_x2 = (0.0, min(C1 / c1, C4 / c4))
        bounds_x3 = (0.0, min(C5 / c5, C2 / c2))

        bounds = bounds_x0, bounds_x1, bounds_x2, bounds_x3

        # args contains all information to solve equation_shgo. This is given to shgo solver
        args = (c1, c2, c3, c4, c5, a1, a2, a3, a4, C1, C2, C3, C4, C5, x_comp["SiO2"], const_K)

        # find the root of the equation
        solutions: Any = shgo(
            func=equation_shgo,
            bounds=bounds,  # type: ignore -- shgo does accept type tuple[tuple[float, float]] at runtime
            args=args,
        )

        # # solution to equation_shgo
        solution_x1: float = solutions.x[0]
        solution_x2: float = solutions.x[1]
        solution_x3: float = solutions.x[2]
        solution_x4: float = solutions.x[3]

        return solution_x1, solution_x2, solution_x3, solution_x4

    def _calc_x_star(
        self,
        params: tuple[
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
        ],
        lists: tuple[list[Any], list[Any], list[Any]],
        solutions: tuple[float, float, float, float],
        x_comp: dict[str, float],
    ):
        c1, c2, c3, c4, c5, a1, a2, a3, a4, C1, C2, C3, C4, C5 = params
        non_sio2, missing_comps, associates = lists
        solution_x1, solution_x2, solution_x3, solution_x4 = solutions

        # mole amounts at equilibrium -- rounded to nullify machine error in subtraction
        n_AlO15 = C1 - c1 * solution_x1 - c1 * solution_x2 - c1 * solution_x3
        n_CaO = C2 - c2 * solution_x1 - c2 * solution_x4
        n_MgO = C3 - c3 * solution_x2
        n_FeO = C4 - c4 * solution_x3
        n_FeO15 = C5 - c5 * solution_x4

        n_CaAl2O4 = a1 * solution_x1
        n_MgAl2O4 = a2 * solution_x2
        n_FeAl2O4 = a3 * solution_x3
        n_CaFe2O4 = a4 * solution_x4

        n_SiO2 = x_comp["SiO2"]

        # derived from eqn 11 - 12 in kim2012-part3
        N_tot = n_AlO15 + n_CaO + n_MgO + n_FeO + n_FeO15 + n_CaAl2O4 + n_MgAl2O4 + n_FeAl2O4 + n_CaFe2O4 + n_SiO2

        # get prime fractions
        X_prime: dict[str, float] = {}

        X_prime["SiO2"] = x_comp["SiO2"] / N_tot

        X_prime[associates[0]] = n_CaAl2O4 / N_tot
        X_prime[associates[1]] = n_MgAl2O4 / N_tot
        X_prime[associates[2]] = n_FeAl2O4 / N_tot
        X_prime[associates[3]] = n_CaFe2O4 / N_tot

        X_prime[non_sio2[0]] = n_AlO15 / N_tot
        X_prime[non_sio2[1]] = n_CaO / N_tot
        X_prime[non_sio2[2]] = n_MgO / N_tot
        X_prime[non_sio2[3]] = n_FeO / N_tot
        X_prime[non_sio2[4]] = n_FeO15 / N_tot

        # eqn 13 in kim2012-part3
        # get number of base cations the associate species constributes
        num_cations_1 = self.equilibrium_stoic[self.names["AlO15"]] / self.equilibrium_stoic[associates[0]]  # CaAl2O4
        num_cations_2 = self.equilibrium_stoic[self.names["AlO15"]] / self.equilibrium_stoic[associates[1]]  # MgAl2O4
        num_cations_3 = self.equilibrium_stoic[self.names["AlO15"]] / self.equilibrium_stoic[associates[2]]  # FeAl2O4
        num_cations_4 = self.equilibrium_stoic[self.names["FeO15"]] / self.equilibrium_stoic[associates[3]]  # CaFe2O4

        N_tot_star = (
            X_prime[non_sio2[0]]  # AlO15
            + X_prime[non_sio2[1]]  # CaO
            + X_prime[non_sio2[2]]  # MgO
            + X_prime[non_sio2[3]]  # FeO
            + X_prime[non_sio2[4]]  # FeO15
            + num_cations_1 * X_prime[associates[0]]  # CaAl2O4
            + num_cations_2 * X_prime[associates[1]]  # MgAl2O4
            + num_cations_3 * X_prime[associates[2]]  # FeAl2O4
            + num_cations_4 * X_prime[associates[3]]  # CaFe2O4
            + X_prime["SiO2"]
        )

        # calculate adjusted composition
        X_star: dict[str, float] = {}
        X_star["SiO2"] = (
            X_prime["SiO2"]
            + num_cations_1 * X_prime[associates[0]]
            + num_cations_2 * X_prime[associates[1]]
            + num_cations_3 * X_prime[associates[2]]
            + num_cations_4 * X_prime[associates[3]]
        ) / N_tot_star  # SiO2
        X_star[non_sio2[0]] = (X_prime[non_sio2[0]]) / N_tot_star  # AlO15
        X_star[non_sio2[1]] = (X_prime[non_sio2[1]]) / N_tot_star  # CaO
        X_star[non_sio2[2]] = (X_prime[non_sio2[2]]) / N_tot_star  # MgO
        X_star[non_sio2[3]] = (X_prime[non_sio2[3]]) / N_tot_star  # FeO
        X_star[non_sio2[4]] = (X_prime[non_sio2[4]]) / N_tot_star  # Fe2O3

        # remove the components not in the input composition
        for comp in missing_comps:
            del X_star[comp]

        return X_star

    def _remove_SiO2(self, comps: list[str]):
        non_sio2_comps: list[str] = []
        for x in comps:
            if x == "SiO2":
                pass
            else:
                non_sio2_comps.append(x)
        return non_sio2_comps

    def _gcd_a_b_c(self, list_coeffs: list[int]):
        options: list[int] = []

        for coeff1 in list_coeffs:
            for coeff2 in list_coeffs:
                options.extend([math.gcd(coeff1, coeff2)])

        gcd: int = min(options)

        c1_new = list_coeffs[0] / gcd
        c2_new = list_coeffs[1] / gcd
        c3_new = list_coeffs[2] / gcd
        c4_new = list_coeffs[3] / gcd
        c5_new = list_coeffs[4] / gcd
        a1_new = list_coeffs[5] / gcd
        a2_new = list_coeffs[6] / gcd
        a3_new = list_coeffs[7] / gcd
        a4_new = list_coeffs[8] / gcd

        return c1_new, c2_new, c3_new, c4_new, c5_new, a1_new, a2_new, a3_new, a4_new

    def _associate_species_will_form(self, x_comp: dict[str, float]):
        if (
            "AlO15" in x_comp
            and x_comp["AlO15"] != 0
            and (
                ("CaO" in x_comp and x_comp["CaO"] != 0)
                or ("MgO" in x_comp and x_comp["MgO"] != 0)
                or ("FeO" in x_comp and x_comp["FeO"] != 0)
            )
        ) or ("FeO15" in x_comp and x_comp["FeO15"] != 0 and ("CaO" in x_comp and x_comp["CaO"] != 0)):
            return True
        else:
            return False


GrundyKimBroschMulti.load_data()
