version = 1.0

NamespaceParser_controls = {}
def registerControl(clsname, modulename):
    # defer the loading of kxmlparser, to reduce launcher start up time 0.07s
    #from Widgets.kxmlparser import NamespaceParser
    NamespaceParser_controls[clsname] = modulename

registerControl('Component', 'Widgets.component')
registerControl('Static', 'Widgets.component')
registerControl('Splitter', 'Widgets.component')
registerControl('Border', 'Widgets.component')

registerControl('Text', 'Widgets.text')

registerControl('Image', 'Widgets.image')

registerControl('Button', 'Widgets.button')
registerControl('TextButton', 'Widgets.button')
registerControl('ImageButton', 'Widgets.button')
registerControl('CheckTextButton', 'Widgets.button')
registerControl('Checkbox', 'Widgets.button')
registerControl('RadioButton', 'Widgets.button')
registerControl('Group', 'Widgets.button')
registerControl('Combobox', 'Widgets.button')

registerControl('StackPanel', 'Widgets.panel')
registerControl('DockSplitter', 'Widgets.panel')
registerControl('DockPanel', 'Widgets.panel')
registerControl('Canvas', 'Widgets.panel')
registerControl('AutoHideCanvas', 'Widgets.panel')
registerControl('GroupCanvas', 'Widgets.panel')
registerControl('Viewbox', 'Widgets.panel')

registerControl('Toolbar', 'Widgets.toolbar')
registerControl('AutoHideToolbar', 'Widgets.toolbar')
registerControl('Captionbar', 'Widgets.toolbar')
registerControl('Caption', 'Widgets.toolbar')

registerControl('PopupBase', 'Widgets.dialog')
registerControl('Dialog', 'Widgets.dialog')

registerControl('Edit', 'Widgets.edit')
registerControl('DatePicker', 'Widgets.datepicker')

registerControl('PopupMenu', 'Widgets.menu')
registerControl('MenuItem', 'Widgets.menu')
registerControl('SelectMenuItem', 'Widgets.menu')
registerControl('MenuSplitter', 'Widgets.menu')
registerControl('Menu', 'Widgets.menu')

registerControl('Menubar', 'Widgets.menubar')
registerControl('PageTray', 'Widgets.menubar')
registerControl('ToolbarTray', 'Widgets.menubar')
registerControl('LabelToolbar', 'Widgets.menubar')
registerControl('LabelButton', 'Widgets.menubar')
registerControl('MenubarItem', 'Widgets.menubar')

registerControl('Progress', 'Widgets.progress')

registerControl('ScrollBar', 'Widgets.scrollbar')

registerControl('Slider', 'Widgets.slider')

registerControl('Window', 'Widgets.window')
