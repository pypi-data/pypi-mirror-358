import sys
import os
import importlib.util
from clyp.transpiler import parse_clyp
from typing import Optional

def clyp_import(module_name: str, current_file_path: Optional[str] = None) -> object:
    """
    Imports a .clyp file as a Python module.
    """
    module_path = module_name.replace('.', os.path.sep) + '.clyp'

    search_paths = []
    if current_file_path:
        search_paths.append(os.path.dirname(current_file_path))
    search_paths.extend(sys.path)
    
    found_path = None
    for path in search_paths:
        potential_path = os.path.join(path, module_path)
        if os.path.exists(potential_path):
            found_path = os.path.abspath(potential_path)
            break
    
    if not found_path:
        raise ImportError(f"Could not find clyp module '{module_name}' at '{module_path}'")

    module_key = f"clyp_module.{found_path}"

    if module_key in sys.modules:
        return sys.modules[module_key]

    with open(found_path, 'r') as f:
        clyp_code = f.read()
    
    python_code = parse_clyp(clyp_code, file_path=found_path)

    spec = importlib.util.spec_from_loader(module_name, loader=None, origin=found_path)
    if spec is None:
        raise ImportError(f"Could not create spec for clyp module '{module_name}'")
        
    module = importlib.util.module_from_spec(spec)
    
    setattr(module, '__file__', found_path)
    
    sys.modules[module_key] = module
    sys.modules[module_name] = module

    exec(python_code, module.__dict__)
    
    return module
