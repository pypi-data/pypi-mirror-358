from rekuest_next.structures.default import id_shrink, get_default_structure_registry
from unlok_next.api.schema import Service, aget_service

structure_reg = get_default_structure_registry()

structure_reg.register_as_structure(
    Service,
    identifier="@lok/service",
    aexpand=aget_service,
    ashrink=id_shrink,
)
