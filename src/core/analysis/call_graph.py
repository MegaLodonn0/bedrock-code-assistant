import jedi
import os
from typing import Set, List, Dict

class DependencyAnalyzer:
    def __init__(self, root_dir: str = '.'):
        self.root_dir = os.path.abspath(root_dir)
        self.project = jedi.Project(self.root_dir)

    def get_impact_files(self, filepath: str) -> Set[str]:
        impacted = {os.path.abspath(filepath)}
        try:
            # Search for references of classes/functions in this file
            with open(filepath, 'r', encoding='utf-8') as f:
                script = jedi.Script(f.read(), path=filepath, project=self.project)
                # Find all defined names (functions, classes)
                for name in script.get_names():
                    # Find all references of these names across the project
                    refs = name.get_references()
                    for ref in refs:
                        if ref.module_path:
                            impacted.add(os.path.abspath(str(ref.module_path)))
        except Exception as e:
            print(f'[WARN] Call Graph Error: {e}')
        return {os.path.relpath(p, self.root_dir) for p in impacted if p.startswith(self.root_dir)}
