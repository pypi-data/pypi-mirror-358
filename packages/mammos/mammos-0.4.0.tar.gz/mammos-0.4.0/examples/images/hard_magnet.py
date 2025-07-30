"""Python program to create the MODA diagram for the hard magnetic workflow."""

import pathlib

import mochada_kit as mk
from mochada_kit.running import run_plantuml_code

themes_dir = mk._THEMES_DIR

puml_code = f"""@startuml
!theme MOCHADA-plasma from {themes_dir}


:Design temperature stable hard magnets; <<user_case_input>>
:Select a material; <<user_case_input>>
split
  group DFT <<group_single>>
    :Load from DFT database; <<data_based_model>>
    :Zero temperature Ms & K; <<processed_output>>
  end group
split again
  group Spin dynamics <<group_single>>
    :Load from SD database; <<data_based_model>>
    :Temperature‐dependent Ms(T); <<processed_output>>
  end group
end split

group analysis <<group_single>>
  :Use Kuzmin model; <<model>>
  :Temperature‐dependent Ms(T), A(T), & K(T); <<processed_output>>
end group

:Select a temperature; <<user_case_input>>

'  Build & run the micromagnetic model
group mumag <<group_single>>
  :Run micromagnetic simulation; <<model>>
  :Output hysteresis loops; <<raw_output>>
end group
'  Post‐processing

group analysis <<group_single>>
  :Extract Hc, Mr, BHmax from loops; <<processed_output>>
end group

@enduml
"""

puml_path = pathlib.Path("hard_magnet_workflow.puml")
puml_path.write_text(puml_code, encoding="utf-8")

run_plantuml_code(
    puml_path,
    output_dir=pathlib.Path("."),
)
