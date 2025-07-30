"""Python program to create the MODA diagram for the sensor workflow."""

import pathlib

import mochada_kit as mk
from mochada_kit.running import run_plantuml_code

themes_dir = mk._THEMES_DIR

puml_code = f"""@startuml
!theme MOCHADA-plasma from {themes_dir}


:Design temperature stable hard magnets; <<user_case_input>>
:Select a material; <<user_case_input>>
group Spin dynamics <<group_single>>
  :Load from SD database; <<data_based_model>>
  :Temperature‐dependent Ms(T); <<processed_output>>
end group

group analysis <<group_single>>
  :Use Kuzmin model; <<model>>
  :Temperature‐dependent Ms(T), A(T), & K(T); <<processed_output>>
end group

:Select a temperature; <<user_case_input>>

'  Build & run the micromagnetic model
group optimization <<group_single>>
repeat
    :Propose new geometry; <<user_case_input>>
    group ubermag <<group_single>>
      :Run micromagnetic simulation; <<model>>
      :Output hysteresis loops; <<raw_output>>
    end group
    '  Post‐processing

    group analysis <<group_single>>
      :Extract linear segment from loops; <<processed_output>>
    end group
repeat while
end group

:Optimal geometry; <<processed_output>>

@enduml
"""

puml_path = pathlib.Path("sensor_workflow.puml")
puml_path.write_text(puml_code, encoding="utf-8")

run_plantuml_code(
    puml_path,
    output_dir=pathlib.Path("."),
)
