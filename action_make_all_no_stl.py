import copy
import working_scad

def main(**kwargs):
    kwargs["run_oomp_populate"] = True

    kwargs["run_oomp"] = True

    kwargs["run_svg"] = True
    kwargs["run_action"] = True
    #kwargs["run_action"] = False

    kwargs["run_scad"] = True

    kwargs["generate_stl"] = False

    import working
    working.run(**kwargs)

if __name__ == '__main__':
    from tool_catalogue import cli_options
    main(**cli_options())