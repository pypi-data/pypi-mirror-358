from brickx.conflicts import CONFLICTS
from brickx.style import Rule, EXTRA_PROPS, StyleSheet
from typing import cast, TypeAlias, override
import hashlib

StyleDict: TypeAlias = dict[str, dict[str, dict[str, str]]]  

class Styler:    
  def __init__(self, *rules: Rule, class_length: int = 7, class_prefix: str = "") -> None:
    self._style: StyleDict = {}
    for rule in rules:
      self.append_rule(rule)

    self.class_length: int = class_length
    self.class_prefix: str = class_prefix
    self.file_name_length: int = 6

  @property
  def style(self) -> StyleDict:
    return self._style
  
  @style.setter
  def style(self, rules: Rule | list[Rule]): 
    if type(rules) in (list, tuple):
      for rule in cast(list[Rule], rules):
        self.append_rule(rule) 
    else:
      self.append_rule(cast(Rule, rules)) 

  def normalize(self, rule: Rule) -> StyleDict:
    rules: StyleDict = {}

    expanded_rule: Rule = {}

    for prop, value in rule.items():
      if prop not in EXTRA_PROPS:
        expanded_rule[prop] = value
      else:
        for p, v in self.expand_extra_prop(prop, [str(value)]).items():
          expanded_rule[p] = v  

    rule = expanded_rule

    media = rule.get("@media", "")
    rules[media] = {}

    for prop, value in rule.items():
      if prop.startswith("@"):
        continue
      elif prop.startswith(":"): # TODO: check for dict
        rules[media] |= self._normalize_pseudo_class(prop, cast(Rule, value))
      else:
        if "" not in rules[media]:
          rules[media][""] = {}

        if type(value) == tuple:
          rules[media][""][prop] = " ".join(value) # TODO: DRY with normalize_pseudo_class
        else:
          rules[media][""][prop] = str(value)

    return rules
  
  def _normalize_pseudo_class(self, pseudo_class: str, rule: Rule, parent: str = "") -> dict[str, dict[str, str]]:
    style: dict[str, dict[str, str]] = {}

    if not pseudo_class.startswith(":"):
      raise TypeError(f'Pseudo class must start with a colon: {pseudo_class}')

    style[pseudo_class] = {}
    for prop, value in rule.items():
      if prop.startswith("@"):
        continue
      elif prop.startswith(":"):
        style |= self._normalize_pseudo_class(pseudo_class + prop, cast(Rule, value), parent)
      else:
        parent += pseudo_class
        if type(value) == tuple:
          style[pseudo_class][prop] = " ".join(value)
        else:  
          style[pseudo_class][prop] = str(value)

    return style
  
  def append_rule(self, rule: Rule): 
    normalized_rule = self.normalize(rule)
    self._style = self.merge_dicts(self._style, normalized_rule)

  def expand_extra_prop(self, prop_name: str, values: list[str]) -> dict[str, str]:
    props: dict[str, str] = {}
    if prop_name in EXTRA_PROPS:
      if len(EXTRA_PROPS[prop_name]) != len(values):
        raise Exception(f"Invalid number of parameters for extra prop: {prop_name}, {values}")

      for i, params in enumerate(EXTRA_PROPS[prop_name]):
        for param in params:
          props[param] = values[i]

    return props 

  @classmethod
  def merge_dicts(cls, dict1: dict, dict2: dict) -> dict:
    result = dict1.copy()
    
    for key, value in dict2.items():
      if key in result and isinstance(result[key], dict) and isinstance(value, dict):
        result[key] = cls.merge_dicts(result[key], value)
      else:
        result[key] = value
    
    return result
  
  def _base_name(self, prop_name: str) -> str:
    return prop_name.split(":")[0]

  def _pseudo_name(self, prop_name: str) -> str:
    parts = prop_name.split(":", 2)
    if len(parts) >= 2:
      return ":" + parts[1] # TODO: DRY ':'
    
    return ""  
  
  def declaration(self, media: str, pseudo: str, prop: str) -> str:
    return f'{prop}: {self._style[media][pseudo][prop]};'
  
  def declarations(self) -> list[str]:
    return []

  def class_name(self, media: str, pseudo: str, prop: str) -> str:
    return ""
  
  def selector(self, media: str, pseudo: str, prop: str) -> str:
    return ""
  
  def classes(self) -> dict: # TODO: review dict
    return {}
  
  def class_names(self) -> list[str]: 
    return []
  
  @classmethod
  def merge_classes(cls, *styles: StyleDict) -> StyleDict: 
    new_layers: StyleDict = {}

    for style in styles:
      new_layers = cls.merge_dicts(new_layers, style)

    return new_layers
  
  def render(self, rules: StyleDict) -> str:
    return ""
  
class InlineStyler(Styler):
  def __init__(self, *rules: Rule) -> None:
    super().__init__(*rules, class_length = 0, class_prefix = "")

  def declarations(self) -> list[str]:
    l: list[str] = []
    for media, pseudos in self._style.items():
      for pseudo, props in pseudos.items():
        if pseudo:
          continue
        
        for prop in props:
          l.append(self.declaration(media, pseudo, prop))

    return l
  
class SpecificStyler(Styler):
  def __init__(self, *rules: Rule, class_length: int = 7, class_prefix: str = "s") -> None:
    super().__init__(*rules, class_length=class_length, class_prefix=class_prefix)

  @override
  def class_name(self, media: str, pseudo: str = "", prop: str = "") -> str:
    return f"{self.class_prefix}" + hashlib.sha1(str(self._style[media]).encode()).hexdigest()[:self.class_length]
  
  override
  def selector(self, media: str, pseudo: str, prop: str = "") -> str:
    return self.class_name(media) + pseudo
  
  @override
  def classes(self) -> StyleDict:
    classes: StyleDict = {}

    for media, pseudo_classes in self._style.items():
      class_name = self.class_name(media)
      classes[media] = {}  # TODO: DRY    

      classes[media][class_name] = {} # TODO: check empty?
      for prop, value in pseudo_classes.items():
          classes[media][class_name + prop] = {}
          for pseudo_prop, pseudo_value in value.items():
            classes[media][class_name + prop][pseudo_prop] = pseudo_value
    return classes
  
  def class_names(self) -> list[str]: 
    names: list[str] = []

    for media in self._style:
      names.append(self.class_name(media).removeprefix(".").strip())

    return names   
  
  def render(self, rules: StyleDict) -> str:
    output = ""

    for media, classes in rules.items():
      indent = 0
      if media:
        media_name = media.removeprefix('"').removesuffix('"')
        output += f'\n@media {media_name} {{\n'
        indent = 2

      for class_name, props in classes.items():
        output += f'{" " * indent}.{class_name} {{\n'
        for prop, value in props.items():
            output += f'  {prop}: {value};\n'

        output += f'{" " * indent}}}\n'  
      output += f'}}\n' if media else ""

    return output
  
class AtomicStyler(Styler):

  def __init__(self, *rules: Rule, class_length: int = 7, class_prefix: str = "a") -> None:
    super().__init__(*rules, class_length=class_length, class_prefix=class_prefix)
  
  @override
  def class_name(self, media: str, pseudo: str, prop: str) -> str:
    declaration = self.declaration(media, pseudo, prop)

    return f"{self.class_prefix}" + hashlib.sha1(str(prop + declaration).encode()).hexdigest()[:self.class_length]
  
  def selector(self, media: str, pseudo: str, prop: str) -> str:
    return self.class_name(media, pseudo, prop) + pseudo
  
  def classes(self) -> StyleDict:
    rules: StyleDict = {}

    for media, pseudos in self._style.items():
      media_conflicts: dict[str, int] = {}

      layers = {}
      for pseudo, props in pseudos.items():
        for prop, value in props.items(): 
          self._resolve(prop, media_conflicts)
          conflict_count = media_conflicts[prop]

          if str(conflict_count) not in layers:
            layers[str(conflict_count)] = {}

          layers[str(conflict_count)][self.selector(media, pseudo, prop)] = {}
          layers[str(conflict_count)][self.selector(media, pseudo, prop)][prop] = value

      rules[media] = layers

    return rules   
  
  def class_names(self) -> list[str]: 
    names: list[str] = []
    layers = self.classes()

    for media, layers in layers.items():
      for i, layer in layers.items():
        for selector in layer:
          suffix = "" if i == "0" else str(i)
          class_name = selector.split(":", 1)[0]
          selector = class_name + suffix
          names.append(selector)

    return names   
  
  def _conflict_count(self, prop_name: str, conflicts: dict[str, int]) -> int:
    name = self._base_name(prop_name)
    sub_props = CONFLICTS[name]
    count = -1

    count = max(count, conflicts.get(name + "$", -1))
    if type(sub_props) == list:
      for sp in sub_props:
        count = max(count, self._conflict_count(sp, conflicts))

    return count  
  
  def _resolve(self, prop: str, conflicts: dict[str, int], layer: int | None = None) -> None:
    sub_props = CONFLICTS[prop]

    if layer is None:
      layer = self._conflict_count(prop, conflicts) + 1
      conflicts[prop] = layer

    conflicts[prop + "$"] = layer

    if type(sub_props) == list:
      for sp in sub_props:
        self._resolve(sp, conflicts, layer) 

  # As a polyfill for layers, selector names are suffixed with the layer number to ensure that the last style always wins.
  def render(self, rules: StyleDict) -> str:
    output = ""
    
    for media, layers in rules.items():
      opening = f'\n@media {media} {{\n' if media else ""
      indent = "  " if media else ""
      closing = f'}}\n' if media else ""

      output += opening
      for i, layer in layers.items():
        for selector, declaration in layer.items():
          suffix = "" if i == "0" else str(i)
          parts = selector.split(":", 1)
          class_name = parts[0]
          pseudo = ""
          if len(parts) >= 2:
            pseudo = ":" + parts[1]

          selector = class_name + suffix + pseudo
          for prop, value in declaration.items(): # TODO: type
            output += f"{indent}.{selector} {{ {prop}: {value}; }}\n"
      output += closing

    return output 
  