# this state is unused to date

# class SlurryState(MaterialState):
#     """
#     The state of a liquid with suspended solids.

#     Args:
#     ----
#         μ : [Pa.s] Liquid fraction dynamic viscosity.
#         ϕ : [m3/m3] Volume fraction solids.
#         pr : Packing ratio of suspended solids.
#     """

#     μ: floatPositive
#     ϕ: floatPositiveOrZero  # TODO: max 0.3
#     pr: floatPositive = 2.94

#     def _init(self):
#         return
