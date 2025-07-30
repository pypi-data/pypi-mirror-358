"""
A degree of freedom calculator based on the Gibbs phase rule -- this might be used in the future.
"""

# def _count_degrees_of_freedom(self):
#     component_elements = {
#         "SiO2": ["Si", "O"],
#         "CaO": ["Ca", "O"],
#         "MgO": ["Mg", "O"],
#         "Al2O3": ["Al", "O"],
#         "FeO": ["Fe", "O"],
#         "Fe2O3": ["Fe", "O"],
#     }

#     number_of_ph = 1 + len(self.a)

#     element_list: list[str] = []
#     for comp in self.x:
#         element_list.extend(component_elements[comp])
#     number_of_elements = len(set(element_list))

#     if "FeO" in self.x or "Fe2O3" in self.x:
#         compositional_constraints = 0
#     else:
#         compositional_constraints = 1

#     dof = 2 + number_of_elements - number_of_ph - compositional_constraints

#     return dof
