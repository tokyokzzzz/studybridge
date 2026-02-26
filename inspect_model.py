import joblib
import numpy as np
import pprint

path = 'D:/study_bridge/ml_models/acceptance_model.joblib'
m = joblib.load(path)

print("=" * 60)
print("MODEL TYPE:")
print(type(m))
print()

print("=" * 60)
print("dir(m):")
print(dir(m))
print()

print("=" * 60)
print("__dict__:")
pprint.pprint(getattr(m, '__dict__', {}))
print()

print("=" * 60)
print("feature_names_in_:")
print(getattr(m, 'feature_names_in_', 'NO FEATURE NAMES'))
print()

print("=" * 60)
print("n_features_in_:")
print(getattr(m, 'n_features_in_', 'NO N_FEATURES'))
print()

print("=" * 60)
print("named_steps (Pipeline check):")
ns = getattr(m, 'named_steps', 'NOT A PIPELINE')
print(ns)
print()

if ns != 'NOT A PIPELINE':
    print("=" * 60)
    print("Pipeline steps detail:")
    for step_name, step_obj in m.named_steps.items():
        print(f"\n  Step: {step_name}")
        print(f"    Type: {type(step_obj)}")
        print(f"    __dict__: ")
        pprint.pprint(getattr(step_obj, '__dict__', {}))
        print(f"    feature_names_in_: {getattr(step_obj, 'feature_names_in_', 'N/A')}")
        print(f"    n_features_in_: {getattr(step_obj, 'n_features_in_', 'N/A')}")

print("=" * 60)
print("classes_:")
print(getattr(m, 'classes_', 'NO CLASSES'))
print()

print("=" * 60)
print("get_params():")
try:
    pprint.pprint(m.get_params())
except Exception as e:
    print(f"Error: {e}")
print()

# Try to get feature importances
print("=" * 60)
print("feature_importances_:")
print(getattr(m, 'feature_importances_', 'NO FEATURE IMPORTANCES'))
print()

print("=" * 60)
print("coef_:")
print(getattr(m, 'coef_', 'NO COEF'))
print()

print("=" * 60)
print("steps (if Pipeline):")
print(getattr(m, 'steps', 'NOT A PIPELINE'))
