import copy

def main(**kwargs):
    kwargs.setdefault("run_oomp_populate", True)
    kwargs.setdefault("run_oomp", True)
    kwargs.setdefault("run_scad", True)
    kwargs.setdefault("run_svg", True)
    kwargs.setdefault("run_action", True)
    kwargs.setdefault("generate_stl", True)
    run(**kwargs)

def run(**kwargs):

    import working_cad
    selected_solidcraft = working_cad.solidcraft_mode(kwargs.get("run_solidcraft", False))
    native_context = dict(kwargs.pop("solidcraft_context", None) or {})
    if kwargs.get("filter"):
        native_context.setdefault("part_filter", kwargs["filter"])
    if selected_solidcraft == "working_scad":
        native_context["recipe_source"] = "working_scad"
    native_context["export_extras"] = kwargs.pop("export_extras", native_context.get("export_extras", False))
    native_context["export_stl"] = kwargs.pop("export_stl", native_context.get("export_stl", False))
    native_context["verify_solidcraft"] = kwargs.pop("verify_solidcraft", native_context.get("verify_solidcraft", False))


    kwargs_2 = copy.deepcopy(kwargs)
    #pop run and generate variables from kwargs
    pop_values = ["run_oomp_populate", "run_oomp", "run_scad", "run_action", "generate_stl", "run_svg", "run_solidcraft", "solidcraft_context"]
    for key in pop_values:
        kwargs_2.pop(key, None)


    if kwargs.get("run_oomp_populate", False):
        import working_oomp_populate
        working_oomp_populate.main(**kwargs_2)

    if kwargs.get("run_oomp", False):
        import working_oomp
        oomp_kwargs = copy.deepcopy(kwargs_2)
        if kwargs.get("run_solidcraft", False):
            oomp_kwargs["wait_for_completion"] = True
        working_oomp.main(**oomp_kwargs)

    if kwargs.get("run_scad", False):        
        kwargs2 = copy.deepcopy(kwargs_2)
        kwargs2["generate_stl"] = kwargs.get("generate_stl", False)
        if kwargs2["generate_stl"]:
            kwargs2["typ"] = "all"
        import working_scad
        working_scad.main(**kwargs2)

    #add run_svg
    if kwargs.get("run_svg", False):        
        import working_svg
        working_svg.main(**kwargs_2)


    if kwargs.get("run_action", False):
        import working_action
        working_action.main(**kwargs)    

    # Opt-in native route runs after legacy actions/OOMP regeneration.
    if kwargs.get("run_solidcraft", False):
        import working_solidcraft
        working_solidcraft.main(solidcraft_context=native_context)




if __name__ == '__main__':
    from tool_catalogue import cli_options
    main(**cli_options())
