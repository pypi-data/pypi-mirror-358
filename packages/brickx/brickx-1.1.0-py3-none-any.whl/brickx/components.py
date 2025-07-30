from brickx.node import Child, Root
from brickx.elements import Doctype, Html, Body, Head

class Document(Root):
  """
  Represents a html document. This is a helper element equivalent to:
  ```
  <!DOCTYPE html>
  <html>
    <head></head>
    <body></body>
  </html>
  ```

  Argument:
    `nodes`: children to pass to the `body` element.

  Properties:
    - `doctype`: returns the `doctype` element
    - `html`: returns the `html` element
    - `head`: returns the `head` element
    - `body`: returns the `body` element
  """

  tag_name: str = "document"
  inline: bool = False

  def __init__(self, *nodes: Child) -> None:
    super().__init__()

    self.doctype = Doctype()
    self.html = Html()
    self.body = Body(*nodes)
    self.head = Head()

    self.doctype + (self.head + self.body >> self.html) >> self