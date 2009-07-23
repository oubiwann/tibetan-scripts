#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""RTEdit
"""
__version__ = '0.0.1'

import gtk, gobject
import gtkdialogs

import os, sys
import thread
import re

try: import i18n
except: import gettext.gettext as _

def get_doctitle(html):
    title = ''
    title = (re.findall(r'''<title>([^\0]*)</title>''', html)+[_("NewDocument")])[0]
    return title


Windows = []
Title = _("RTEdit")

class MainWindow:
    def __init__(self, editfile='', create = True, accel_group = None, tooltips = None):
        self.editfile = editfile
        ## 考虑已经打开文档的情况
        if editfile:
            for i in Windows:
                if i.editfile == editfile:
                    print _('File "%s" already opened') % editfile
                    i.window.show()
                    i.window.present()
                    #@TODO: 让 edit 获得焦点
                    i.window.grab_focus()
                    i.edit.get_child().grab_focus()
                    del self
                    return
                pass
            pass
        ##
        Windows.append(self)
        import gtkwebedit # 推迟 import gtkwebedit
        ##
        if accel_group is None:
            self.accel_group = gtk.AccelGroup()
        else:
            self.accel_group = accel_group
        if tooltips is None:
            self.tooltips = gtk.Tooltips()
        else:
            self.tooltips = tooltips
        self.tooltips.enable()
        if create:
            self.window = gtk.Window()
            gtk.window_set_default_icon_name("gtk-dnd")
            self.window.set_icon_name("gtk-dnd")
            self.window.set_default_size(500,500)
            self.window.set_title(Title)
            if editfile: self.window.set_title(os.path.basename(self.editfile) + ' - ' + Title) 
            self.window.add_accel_group(self.accel_group)
            self.window.show()
            self.window.connect("delete_event", self.on_close)

        self.vbox1 = gtk.VBox(False, 0)
        self.vbox1.show()

        self.menubar1 = gtk.MenuBar()
        self.menubar1.show()

        self.menuitem_file = gtk.MenuItem(_("_File"))
        self.menuitem_file.show()

        self.menu_file = gtk.Menu()
        self.menu_file.append(gtk.TearoffMenuItem())

        self.menuitem_new = gtk.ImageMenuItem("gtk-new")
        self.menuitem_new.show()
        self.menuitem_new.connect("activate", self.on_new)
        self.menuitem_new.add_accelerator("activate", self.accel_group, gtk.gdk.keyval_from_name("n"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)


        self.menu_file.append(self.menuitem_new)

        self.menuitem_open = gtk.ImageMenuItem("gtk-open")
        self.menuitem_open.show()
        self.menuitem_open.connect("activate", self.on_open)
        self.menuitem_open.add_accelerator("activate", self.accel_group, gtk.gdk.keyval_from_name("o"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)


        self.menu_file.append(self.menuitem_open)

        self.menuitem_save = gtk.ImageMenuItem("gtk-save")
        self.menuitem_save.show()
        self.menuitem_save.connect("activate", self.on_save)
        self.menuitem_save.add_accelerator("activate", self.accel_group, gtk.gdk.keyval_from_name("s"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)


        self.menu_file.append(self.menuitem_save)

        self.menuitem_save_as = gtk.ImageMenuItem("gtk-save-as")
        self.menuitem_save_as.show()
        self.menuitem_save_as.connect("activate", self.on_save_as)

        self.menu_file.append(self.menuitem_save_as)

        #self.menuitem_separator1 = gtk.MenuItem()
        #self.menuitem_separator1.show()
        #
        #self.menu_file.append(self.menuitem_separator1)
        #
        #self.menuitem_print = gtk.ImageMenuItem("gtk-print")
        #self.menuitem_print.show()
        #self.menuitem_print.connect("activate", self.on_print)
        #
        #self.menu_file.append(self.menuitem_print)

        self.menu_file.append(gtk.MenuItem())

        ## 最近使用文件菜单 ################
        self.recent = gtk.RecentManager()
        self.menu_recent = gtk.RecentChooserMenu(self.recent)
        self.menu_recent.set_limit(25)
        if editfile: self.add_recent(editfile)
        ##
        self.file_filter = gtk.RecentFilter()
        self.file_filter.add_mime_type("text/html")
        self.menu_recent.set_filter(self.file_filter)

        self.menu_recent.connect("item-activated", self.on_select_recent)
        self.menuitem_recent = gtk.ImageMenuItem(_("_Recently"))
        self.menuitem_recent.set_image(gtk.image_new_from_icon_name("document-open-recent", gtk.ICON_SIZE_MENU))

        self.menuitem_recent.set_submenu(self.menu_recent)
        self.menu_file.append(self.menuitem_recent)
        #####################################

        self.menuitem_separatormenuitem1 = gtk.MenuItem()
        self.menuitem_separatormenuitem1.show()

        self.menu_file.append(self.menuitem_separatormenuitem1)

        self.menuitem_close = gtk.ImageMenuItem("gtk-close")
        self.menuitem_close.show()
        self.menuitem_close.connect("activate", self.on_close)
        self.menuitem_close.add_accelerator("activate", self.accel_group, gtk.gdk.keyval_from_name("w"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)


        self.menu_file.append(self.menuitem_close)

        self.menuitem_quit = gtk.ImageMenuItem("gtk-quit")
        self.menuitem_quit.show()
        self.menuitem_quit.connect("activate", self.on_quit)
        self.menuitem_quit.add_accelerator("activate", self.accel_group, gtk.gdk.keyval_from_name("q"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)


        self.menu_file.append(self.menuitem_quit)

        self.menuitem_file.set_submenu(self.menu_file)

        self.menubar1.append(self.menuitem_file)

        self.menuitem_edit = gtk.MenuItem(_("_Edit"))
        self.menuitem_edit.show()

        self.menu_edit = gtk.Menu()
        self.menu_edit.append(gtk.TearoffMenuItem())

        self.menuitem_undo = gtk.ImageMenuItem("gtk-undo")
        self.menuitem_undo.show()
        self.menuitem_undo.connect("activate", self.do_undo)

        self.menu_edit.append(self.menuitem_undo)

        self.menuitem_redo = gtk.ImageMenuItem("gtk-redo")
        self.menuitem_redo.show()
        self.menuitem_redo.connect("activate", self.do_redo)

        self.menu_edit.append(self.menuitem_redo)

        self.menuitem_separator2 = gtk.MenuItem()
        self.menuitem_separator2.show()

        self.menu_edit.append(self.menuitem_separator2)

        self.menuitem_cut = gtk.ImageMenuItem("gtk-cut")
        self.menuitem_cut.show()
        self.menuitem_cut.connect("activate", self.do_cut)

        self.menu_edit.append(self.menuitem_cut)

        self.menuitem_copy = gtk.ImageMenuItem("gtk-copy")
        self.menuitem_copy.show()
        self.menuitem_copy.connect("activate", self.do_copy)

        self.menu_edit.append(self.menuitem_copy)

        self.menuitem_paste = gtk.ImageMenuItem("gtk-paste")
        self.menuitem_paste.show()
        self.menuitem_paste.connect("activate", self.do_paste)

        self.menu_edit.append(self.menuitem_paste)

        self.menuitem_delete = gtk.ImageMenuItem("gtk-delete")
        self.menuitem_delete.show()
        self.menuitem_delete.connect("activate", self.do_delete)

        self.menu_edit.append(self.menuitem_delete)

        self.menuitem_separator3 = gtk.MenuItem()
        self.menuitem_separator3.show()

        self.menu_edit.append(self.menuitem_separator3)

        self.menuitem_select_all = gtk.ImageMenuItem("gtk-select-all")
        self.menuitem_select_all.show()
        self.menuitem_select_all.connect("activate", self.do_selectall)

        self.menu_edit.append(self.menuitem_select_all)

        self.menuitem_separator12 = gtk.MenuItem()
        self.menuitem_separator12.show()

        self.menu_edit.append(self.menuitem_separator12)

        self.menuitem_find = gtk.ImageMenuItem("gtk-find")
        self.menuitem_find.show()
        self.menuitem_find.connect("activate", self.show_findbar)
        self.menuitem_find.add_accelerator("activate", self.accel_group, gtk.gdk.keyval_from_name("f"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)


        self.menu_edit.append(self.menuitem_find)

        self.menuitem_find_and_replace = gtk.ImageMenuItem("gtk-find-and-replace")
        self.menuitem_find_and_replace.show()
        self.menuitem_find_and_replace.connect("activate", self.show_findbar)

        self.menu_edit.append(self.menuitem_find_and_replace)

        self.menuitem_edit.set_submenu(self.menu_edit)

        self.menubar1.append(self.menuitem_edit)

        self.menuitem_view = gtk.MenuItem(_("_View"))
        self.menuitem_view.show()

        self.menu_view = gtk.Menu()
        self.menu_view.append(gtk.TearoffMenuItem())

        self.menuitem_update_contents = gtk.ImageMenuItem(_("Update _Contents"))
        self.menuitem_update_contents.show()
        self.menuitem_update_contents.connect("activate", self.view_update_contents)

        img = gtk.image_new_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
        self.menuitem_update_contents.set_image(img)
        self.menu_view.append(self.menuitem_update_contents)

        self.menuitem_toggle_numbered_title = gtk.ImageMenuItem(_("Toggle _Numbered Title"))
        self.menuitem_toggle_numbered_title.show()
        self.menuitem_toggle_numbered_title.connect("activate", self.view_toggle_autonumber)

        img = gtk.image_new_from_stock(gtk.STOCK_SORT_DESCENDING, gtk.ICON_SIZE_MENU)
        self.menuitem_toggle_numbered_title.set_image(img)
        self.menu_view.append(self.menuitem_toggle_numbered_title)

        self.menuitem_update_images = gtk.ImageMenuItem(_("Update _Images"))
        self.menuitem_update_images.show()
        self.menuitem_update_images.connect("activate", self.do_update_images)

        img = gtk.image_new_from_icon_name('stock_insert_image', gtk.ICON_SIZE_MENU)
        self.menuitem_update_images.set_image(img)
        self.menu_view.append(self.menuitem_update_images)

        self.menuitem_separator10 = gtk.MenuItem()
        self.menuitem_separator10.show()

        self.menu_view.append(self.menuitem_separator10)

        self.menuitem_view_source = gtk.ImageMenuItem(_("So_urce"))
        self.menuitem_view_source.show()
        self.menuitem_view_source.connect("activate", self.view_sourceview)
        self.menuitem_view_source.add_accelerator("activate", self.accel_group, gtk.gdk.keyval_from_name("u"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

        img = gtk.image_new_from_icon_name('stock_view-html-source', gtk.ICON_SIZE_MENU)
        self.menuitem_view_source.set_image(img)
        self.menu_view.append(self.menuitem_view_source)

        self.menuitem_view.set_submenu(self.menu_view)

        self.menubar1.append(self.menuitem_view)

        self.menuitem_insert = gtk.MenuItem(_("_Insert"))
        self.menuitem_insert.show()

        self.menu_insert = gtk.Menu()
        self.menu_insert.append(gtk.TearoffMenuItem())

        self.menuitem_picture = gtk.ImageMenuItem(_("_Picture"))
        self.menuitem_picture.show()
        self.menuitem_picture.connect("activate", self.do_insertimage)

        img = gtk.image_new_from_icon_name('stock_insert_image', gtk.ICON_SIZE_MENU)
        self.menuitem_picture.set_image(img)
        self.menu_insert.append(self.menuitem_picture)

        self.menuitem_link = gtk.ImageMenuItem(_("_Link"))
        self.menuitem_link.show()
        self.menuitem_link.connect("activate", self.do_createlink)

        img = gtk.image_new_from_icon_name('stock_link', gtk.ICON_SIZE_MENU)
        self.menuitem_link.set_image(img)
        self.menu_insert.append(self.menuitem_link)

        self.menuitem_horizontalrule = gtk.ImageMenuItem(_("Horizontal_Rule"))
        self.menuitem_horizontalrule.show()
        self.menuitem_horizontalrule.connect("activate", self.do_inserthorizontalrule)

        img = gtk.image_new_from_icon_name('stock_insert-rule', gtk.ICON_SIZE_MENU)
        self.menuitem_horizontalrule.set_image(img)
        self.menu_insert.append(self.menuitem_horizontalrule)

        self.menuitem_insert_table = gtk.ImageMenuItem(_("_Table"))
        self.menuitem_insert_table.show()
        self.menuitem_insert_table.connect("activate", self.do_insert_table)

        img = gtk.image_new_from_icon_name('stock_insert-table', gtk.ICON_SIZE_MENU)
        self.menuitem_insert_table.set_image(img)
        self.menu_insert.append(self.menuitem_insert_table)

        self.menuitem_insert_html = gtk.ImageMenuItem(_("_HTML"))
        self.menuitem_insert_html.show()
        self.menuitem_insert_html.connect("activate", self.do_inserthtml)

        img = gtk.image_new_from_icon_name('stock_view-html-source', gtk.ICON_SIZE_MENU)
        self.menuitem_insert_html.set_image(img)
        self.menu_insert.append(self.menuitem_insert_html)

        self.menuitem_separator9 = gtk.MenuItem()
        self.menuitem_separator9.show()

        self.menu_insert.append(self.menuitem_separator9)

        self.menuitem_insert_contents = gtk.ImageMenuItem(_("_Contents"))
        self.menuitem_insert_contents.show()
        self.menuitem_insert_contents.connect("activate", self.do_insert_contents)

        img = gtk.image_new_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
        self.menuitem_insert_contents.set_image(img)
        self.menu_insert.append(self.menuitem_insert_contents)

        self.menuitem_insert.set_submenu(self.menu_insert)

        self.menubar1.append(self.menuitem_insert)

        self.menuitem_style = gtk.MenuItem(_("_Style"))
        self.menuitem_style.show()

        self.menu_style = gtk.Menu()
        self.menu_style.append(gtk.TearoffMenuItem())

        self.menuitem_normal = gtk.ImageMenuItem(_("_Normal"))
        self.menuitem_normal.show()
        self.menuitem_normal.connect("activate", self.do_formatblock_p)

        img = gtk.image_new_from_icon_name('stock_insert_section', gtk.ICON_SIZE_MENU)
        self.menuitem_normal.set_image(img)
        self.menu_style.append(self.menuitem_normal)

        self.menuitem_separator4 = gtk.MenuItem()
        self.menuitem_separator4.show()

        self.menu_style.append(self.menuitem_separator4)

        self.menuitem_heading_1 = gtk.ImageMenuItem(_("Heading _1"))
        self.menuitem_heading_1.show()
        self.menuitem_heading_1.connect("activate", self.do_formatblock_h1)

        img = gtk.image_new_from_icon_name('stock_insert-header', gtk.ICON_SIZE_MENU)
        self.menuitem_heading_1.set_image(img)
        self.menu_style.append(self.menuitem_heading_1)

        self.menuitem_heading_2 = gtk.ImageMenuItem(_("Heading _2"))
        self.menuitem_heading_2.show()
        self.menuitem_heading_2.connect("activate", self.do_formatblock_h2)

        img = gtk.image_new_from_icon_name('stock_line-spacing-2', gtk.ICON_SIZE_MENU)
        self.menuitem_heading_2.set_image(img)
        self.menu_style.append(self.menuitem_heading_2)

        self.menuitem_heading_3 = gtk.ImageMenuItem(_("Heading _3"))
        self.menuitem_heading_3.show()
        self.menuitem_heading_3.connect("activate", self.do_formatblock_h3)

        img = gtk.image_new_from_icon_name('stock_line-spacing-1', gtk.ICON_SIZE_MENU)
        self.menuitem_heading_3.set_image(img)
        self.menu_style.append(self.menuitem_heading_3)

        self.menuitem_heading_4 = gtk.ImageMenuItem(_("Heading _4"))
        self.menuitem_heading_4.show()
        self.menuitem_heading_4.connect("activate", self.do_formatblock_h4)

        img = gtk.image_new_from_icon_name('stock_line-spacing-1.5', gtk.ICON_SIZE_MENU)
        self.menuitem_heading_4.set_image(img)
        self.menu_style.append(self.menuitem_heading_4)

        self.menuitem_heading_5 = gtk.ImageMenuItem(_("Heading _5"))
        self.menuitem_heading_5.show()
        self.menuitem_heading_5.connect("activate", self.do_formatblock_h5)

        img = gtk.image_new_from_icon_name('stock_list_enum-off', gtk.ICON_SIZE_MENU)
        self.menuitem_heading_5.set_image(img)
        self.menu_style.append(self.menuitem_heading_5)

        self.menuitem_heading_6 = gtk.ImageMenuItem(_("Heading _6"))
        self.menuitem_heading_6.show()
        self.menuitem_heading_6.connect("activate", self.do_formatblock_h6)

        img = gtk.image_new_from_icon_name('stock_list_enum-off', gtk.ICON_SIZE_MENU)
        self.menuitem_heading_6.set_image(img)
        self.menu_style.append(self.menuitem_heading_6)

        self.menuitem_separator5 = gtk.MenuItem()
        self.menuitem_separator5.show()

        self.menu_style.append(self.menuitem_separator5)

        self.menuitem_bulleted_list = gtk.ImageMenuItem(_("_Bulleted List"))
        self.menuitem_bulleted_list.show()
        self.menuitem_bulleted_list.connect("activate", self.do_insertunorderedlist)

        img = gtk.image_new_from_icon_name('stock_list_bullet', gtk.ICON_SIZE_MENU)
        self.menuitem_bulleted_list.set_image(img)
        self.menu_style.append(self.menuitem_bulleted_list)

        self.menuitem_numbered_list = gtk.ImageMenuItem(_("Numbered _List"))
        self.menuitem_numbered_list.show()
        self.menuitem_numbered_list.connect("activate", self.do_insertorderedlist)

        img = gtk.image_new_from_icon_name('stock_list_enum', gtk.ICON_SIZE_MENU)
        self.menuitem_numbered_list.set_image(img)
        self.menu_style.append(self.menuitem_numbered_list)

        self.menuitem_separator6 = gtk.MenuItem()
        self.menuitem_separator6.show()

        self.menu_style.append(self.menuitem_separator6)

        self.address1 = gtk.ImageMenuItem(_("A_ddress"))
        self.address1.show()
        self.address1.connect("activate", self.do_formatblock_address)

        img = gtk.image_new_from_icon_name('stock_tools-hyphenation', gtk.ICON_SIZE_MENU)
        self.address1.set_image(img)
        self.menu_style.append(self.address1)

        #self.menuitem_formatblock_code = gtk.ImageMenuItem(_("_Code"))
        #self.menuitem_formatblock_code.show()
        #self.menuitem_formatblock_code.connect("activate", self.do_formatblock_code)
        #
        #img = gtk.image_new_from_icon_name('stock_text-monospaced', gtk.ICON_SIZE_MENU)
        #self.menuitem_formatblock_code.set_image(img)
        #self.menu_style.append(self.menuitem_formatblock_code)

        self.menuitem_formatblock_blockquote = gtk.ImageMenuItem(_("Block_quote"))
        self.menuitem_formatblock_blockquote.show()
        self.menuitem_formatblock_blockquote.connect("activate", self.do_formatblock_blockquote)

        img = gtk.image_new_from_icon_name('stock_list-insert-unnumbered', gtk.ICON_SIZE_MENU)
        self.menuitem_formatblock_blockquote.set_image(img)
        self.menu_style.append(self.menuitem_formatblock_blockquote)

        self.menuitem_formatblock_pre = gtk.ImageMenuItem(_("_Preformat"))
        self.menuitem_formatblock_pre.show()
        self.menuitem_formatblock_pre.connect("activate", self.do_formatblock_pre)

        img = gtk.image_new_from_icon_name('stock_text-quickedit', gtk.ICON_SIZE_MENU)
        self.menuitem_formatblock_pre.set_image(img)
        self.menu_style.append(self.menuitem_formatblock_pre)

        self.menuitem_style.set_submenu(self.menu_style)

        self.menubar1.append(self.menuitem_style)

        self.menuitem_format = gtk.MenuItem(_("For_mat"))
        self.menuitem_format.show()

        self.menu_format = gtk.Menu()
        self.menu_format.append(gtk.TearoffMenuItem())

        self.menuitem_bold = gtk.ImageMenuItem("gtk-bold")
        self.menuitem_bold.show()
        self.menuitem_bold.connect("activate", self.on_bold)
        self.menuitem_bold.add_accelerator("activate", self.accel_group, gtk.gdk.keyval_from_name("b"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

        self.menu_format.append(self.menuitem_bold)

        self.menuitem_underline = gtk.ImageMenuItem("gtk-underline")
        self.menuitem_underline.show()
        self.menuitem_underline.connect("activate", self.do_underline)

        self.menu_format.append(self.menuitem_underline)

        self.menuitem_italic = gtk.ImageMenuItem("gtk-italic")
        self.menuitem_italic.show()
        self.menuitem_italic.connect("activate", self.do_italic)

        self.menu_format.append(self.menuitem_italic)

        self.menuitem_strikethrough = gtk.ImageMenuItem("gtk-strikethrough")
        self.menuitem_strikethrough.show()
        self.menuitem_strikethrough.connect("activate", self.do_strikethrough)

        self.menu_format.append(self.menuitem_strikethrough)

        self.separator7 = gtk.MenuItem()
        self.separator7.show()

        self.menu_format.append(self.separator7)

        self.menuitem_font_fontname = gtk.ImageMenuItem("gtk-select-font")
        self.menuitem_font_fontname.show()
        #self.menuitem_font_fontname.connect("activate", self.do_font_fontname)

        ## 字体列表菜单 #########################################
        self.fontname_menu = gtk.Menu()
        self.fontname_menu.append(gtk.TearoffMenuItem())
        fontnames = sorted(( familie.get_name() for familie in gtk.Label().get_pango_context().list_families() ))
        for fontname in ['Serif', 'Sans', 'Sans-serif', 'Monospace', ''] + fontnames:
            if fontname:
                menu = gtk.MenuItem(fontname)
                menu.connect("activate", self.do_font_fontname, fontname)
                pass
            else:
                menu = gtk.MenuItem()
                pass
            menu.show()
            self.fontname_menu.append(menu)
            pass
        self.fontname_menu.show()
        self.menuitem_font_fontname.set_submenu(self.fontname_menu)
        ###########################################

        self.menu_format.append(self.menuitem_font_fontname)

        self.menuitem_font_size = gtk.ImageMenuItem(_("Font _Size"))
        self.menuitem_font_size.show()

        img = gtk.image_new_from_icon_name('stock_font-size', gtk.ICON_SIZE_MENU)
        self.menuitem_font_size.set_image(img)
        self.font_size1_menu = gtk.Menu()
        self.font_size1_menu.append(gtk.TearoffMenuItem())

        self.menuitem_fontsize_1 = gtk.MenuItem(_("_1"))
        self.menuitem_fontsize_1.show()
        self.menuitem_fontsize_1.connect("activate", self.do_fontsize_1)

        self.font_size1_menu.append(self.menuitem_fontsize_1)

        self.menuitem_fontsize_2 = gtk.MenuItem(_("_2"))
        self.menuitem_fontsize_2.show()
        self.menuitem_fontsize_2.connect("activate", self.do_fontsize_2)

        self.font_size1_menu.append(self.menuitem_fontsize_2)

        self.menuitem_fontsize_3 = gtk.MenuItem(_("_3"))
        self.menuitem_fontsize_3.show()
        self.menuitem_fontsize_3.connect("activate", self.do_fontsize_3)

        self.font_size1_menu.append(self.menuitem_fontsize_3)

        self.menuitem_fontsize_4 = gtk.MenuItem(_("_4"))
        self.menuitem_fontsize_4.show()
        self.menuitem_fontsize_4.connect("activate", self.do_fontsize_4)

        self.font_size1_menu.append(self.menuitem_fontsize_4)

        self.menuitem_fontsize_5 = gtk.MenuItem(_("_5"))
        self.menuitem_fontsize_5.show()
        self.menuitem_fontsize_5.connect("activate", self.do_fontsize_5)

        self.font_size1_menu.append(self.menuitem_fontsize_5)

        self.menuitem_fontsize_6 = gtk.MenuItem(_("_6"))
        self.menuitem_fontsize_6.show()
        self.menuitem_fontsize_6.connect("activate", self.do_fontsize_6)

        self.font_size1_menu.append(self.menuitem_fontsize_6)

        self.menuitem_fontsize_7 = gtk.MenuItem(_("_7"))
        self.menuitem_fontsize_7.show()
        self.menuitem_fontsize_7.connect("activate", self.do_fontsize_7)

        self.font_size1_menu.append(self.menuitem_fontsize_7)

        self.menuitem_font_size.set_submenu(self.font_size1_menu)

        self.menu_format.append(self.menuitem_font_size)

        self.menuitem_color = gtk.ImageMenuItem("gtk-select-color")
        self.menuitem_color.show()
        self.menuitem_color.connect("activate", self.on_color_select_forecolor)

        self.menu_format.append(self.menuitem_color)

        self.menuitem_bg_color = gtk.ImageMenuItem(_("_Highlight"))
        self.menuitem_bg_color.show()
        self.menuitem_bg_color.connect("activate", self.do_color_hilitecolor)
        self.menuitem_bg_color.add_accelerator("activate", self.accel_group, gtk.gdk.keyval_from_name("h"), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

        img = gtk.image_new_from_icon_name('stock_text_color_hilight', gtk.ICON_SIZE_MENU)
        self.menuitem_bg_color.set_image(img)
        self.menu_format.append(self.menuitem_bg_color)

        self.menuitem_bg_color_select = gtk.ImageMenuItem(_("_HiliteColor"))
        self.menuitem_bg_color_select.show()
        self.menuitem_bg_color_select.connect("activate", self.on_color_select_hilitecolor)

        img = gtk.image_new_from_stock(gtk.STOCK_SELECT_COLOR, gtk.ICON_SIZE_MENU)
        self.menuitem_bg_color_select.set_image(img)
        self.menu_format.append(self.menuitem_bg_color_select)

        self.menuitem_clearformat = gtk.ImageMenuItem("gtk-clear")
        self.menuitem_clearformat.show()
        self.menuitem_clearformat.connect("activate", self.do_removeformat)

        self.menu_format.append(self.menuitem_clearformat)

        self.separator8 = gtk.MenuItem()
        self.separator8.show()

        self.menu_format.append(self.separator8)

        self.menuitem_justifyleft = gtk.ImageMenuItem("gtk-justify-left")
        self.menuitem_justifyleft.show()
        self.menuitem_justifyleft.connect("activate", self.do_justifyleft)

        self.menu_format.append(self.menuitem_justifyleft)

        self.menuitem_justifycenter = gtk.ImageMenuItem("gtk-justify-center")
        self.menuitem_justifycenter.show()
        self.menuitem_justifycenter.connect("activate", self.do_justifycenter)

        self.menu_format.append(self.menuitem_justifycenter)

        self.menuitem_justifyright = gtk.ImageMenuItem("gtk-justify-right")
        self.menuitem_justifyright.show()
        self.menuitem_justifyright.connect("activate", self.do_justifyright)

        self.menu_format.append(self.menuitem_justifyright)

        self.separator11 = gtk.MenuItem()
        self.separator11.show()

        self.menu_format.append(self.separator11)

        self.menuitem_increase_indent = gtk.ImageMenuItem("gtk-indent")
        self.menuitem_increase_indent.show()
        self.menuitem_increase_indent.connect("activate", self.do_indent)

        self.menu_format.append(self.menuitem_increase_indent)

        self.menuitem_decrease_indent = gtk.ImageMenuItem("gtk-unindent")
        self.menuitem_decrease_indent.show()
        self.menuitem_decrease_indent.connect("activate", self.do_outdent)

        self.menu_format.append(self.menuitem_decrease_indent)

        self.separator16 = gtk.MenuItem()
        self.separator16.show()

        self.menu_format.append(self.separator16)

        self.menuitem_subscript = gtk.ImageMenuItem(_("Subs_cript"))
        self.menuitem_subscript.show()
        self.menuitem_subscript.connect("activate", self.do_subscript)

        img = gtk.image_new_from_icon_name('stock_subscript', gtk.ICON_SIZE_MENU)
        self.menuitem_subscript.set_image(img)
        self.menu_format.append(self.menuitem_subscript)

        self.menuitem_superscript = gtk.ImageMenuItem(_("Su_perscript"))
        self.menuitem_superscript.show()
        self.menuitem_superscript.connect("activate", self.do_superscript)

        img = gtk.image_new_from_icon_name('stock_superscript', gtk.ICON_SIZE_MENU)
        self.menuitem_superscript.set_image(img)
        self.menu_format.append(self.menuitem_superscript)

        self.menuitem_format.set_submenu(self.menu_format)

        self.menubar1.append(self.menuitem_format)

        self.menuitem_help = gtk.MenuItem(_("_Help"))
        self.menuitem_help.show()

        self.menu_help = gtk.Menu()
        self.menu_help.append(gtk.TearoffMenuItem())

        self.menuitem_about = gtk.ImageMenuItem("gtk-about")
        self.menuitem_about.show()
        self.menuitem_about.connect("activate", self.on_about)

        self.menu_help.append(self.menuitem_about)

        self.menuitem_help.set_submenu(self.menu_help)

        self.menubar1.append(self.menuitem_help)

        self.menubar1.show_all()

        self.vbox1.pack_start(self.menubar1, False, False, 0)

        #self.editport = gtk.Viewport()
        #self.editport.show()
        #self.editport.set_shadow_type(gtk.SHADOW_NONE)
        #
        #self.vbox1.pack_start(self.editport)

        self.edit = gtkwebedit.WebEdit(self.editfile)
        self.edit.show_all()
        self.vbox1.pack_start(self.edit)
        self.edit.set_flags(gtk.CAN_DEFAULT)
        self.window.present()

        self.findbar = gtk.HandleBox()
        self.findbar.set_shadow_type(gtk.SHADOW_OUT)

        self.findbox = gtk.HBox(False, 0)
        self.findbox.show()

        self.button_hidefindbar = gtk.Button()
        self.button_hidefindbar.set_tooltip_text(_("Close Findbar"))
        self.button_hidefindbar.show()
        self.button_hidefindbar.set_relief(gtk.RELIEF_NONE)
        self.button_hidefindbar.connect("clicked", self.hide_findbar)

        self.image113 = gtk.Image()
        self.image113.set_from_stock(gtk.STOCK_CLOSE, 1)
        self.image113.show()
        self.button_hidefindbar.add(self.image113)

        self.findbox.pack_start(self.button_hidefindbar, False, False, 0)

        self.entry_searchtext = gtk.Entry()
        self.entry_searchtext.show()
        #self.entry_searchtext.set_flags(gtk.CAN_DEFAULT)
        #self.entry_searchtext.grab_focus()
        self.findbox.pack_start(self.entry_searchtext)

        self.button1 = gtk.Button()
        self.tooltips.set_tip(self.button1, _("Find Previous"))
        self.button1.show()
        self.button1.connect("clicked", self.do_find_text_forward)

        self.image1 = gtk.Image()
        self.image1.set_from_stock(gtk.STOCK_GO_BACK, 4)
        self.image1.show()
        self.button1.add(self.image1)

        self.findbox.pack_start(self.button1, False, False, 0)

        self.button_search_text = gtk.Button(None, gtk.STOCK_FIND)
        self.tooltips.set_tip(self.button_search_text, _("Find Next"))
        self.button_search_text.show()
        self.button_search_text.connect("clicked", self.do_find_text)

        self.findbox.pack_start(self.button_search_text, False, False, 0)

        self.entry_replace_text = gtk.Entry()
        self.entry_replace_text.show()
        self.findbox.pack_start(self.entry_replace_text)

        self.button_replace_text = gtk.Button()
        self.tooltips.set_tip(self.button_replace_text, _("Replace"))
        self.button_replace_text.show()
        self.button_replace_text.connect("clicked", self.do_replace_text)

        self.alignment1 = gtk.Alignment(0.5, 0.5, 0, 0)
        self.alignment1.show()

        self.hbox2 = gtk.HBox(False, 0)
        self.hbox2.show()
        self.hbox2.set_spacing(2)

        self.image136 = gtk.Image()
        self.image136.set_from_stock(gtk.STOCK_FIND_AND_REPLACE, 4)
        self.image136.show()
        self.hbox2.pack_start(self.image136, False, False, 0)

        self.label1 = gtk.Label(_("Replace"))
        self.label1.show()
        self.hbox2.pack_start(self.label1, False, False, 0)

        self.alignment1.add(self.hbox2)

        self.button_replace_text.add(self.alignment1)

        self.findbox.pack_start(self.button_replace_text, False, False, 0)

        self.button2 = gtk.Button()
        self.tooltips.set_tip(self.button2, _("Replace All"))
        self.button2.set_label(_("ReplaceAll"))
        self.button2.show()
        self.button2.connect("clicked", self.do_replace_text_all)

        self.findbox.pack_start(self.button2, False, False, 0)

        self.findbar.add(self.findbox)

        self.vbox1.pack_start(self.findbar, False, False, 0)


        ##
        self.edit.on_html_save = self.on_html_save
        self.edit.on_html_saveas = self.on_html_saveas

        #self.edit.contextmenu.append(self.menuitem_style)

        self.edit.connect("popup-menu", self._populate_popup)


        if create:
            self.window.add(self.vbox1)

    def _populate_popup(self, edit):
        menu = edit.contextmenu

    def on_close(self, *args):
        print 'on_close:', self
        #@TODO: 退出时未保存提示
        Windows.remove(self)
        gtk.gdk.threads_leave()
        self.window.destroy()
        if not Windows:
            gtk.main_quit() 
        pass

    def on_quit(self, *args):
        print 'on_quit:'
        windows = reversed(Windows)
        for window in windows:
            window.on_close()
            pass
        gtk.main_quit()
        pass

    def on_new(self, *args):
        print 'on_new:'
        MainWindow()
        pass

    def add_recent(self, filename):
        uri = 'file://' + filename
        self.recent.add_full(uri, {'mime_type':'text/html', 'app_name':'rtedit', 'app_exec':'rtedit', 'group':'rtedit'})

    def on_select_recent(self, menu):
        filename = menu. get_current_item().get_uri_display()
        print 'on_select_recent:', filename
        MainWindow(editfile = filename)

    def on_open(self, *args):
        print 'on_open:'
        filename = gtkdialogs.open(title=_('Open'), name_mimes={_("Html Document"):"text/html"})
        if filename and os.access(filename, os.R_OK):
            MainWindow(editfile = filename)
            pass
        gtk.gdk.threads_leave()
        pass

    def on_save(self, *args):
        print 'on_save:'
        self.edit.do_html_save()
        pass

    def on_html_save(self, html):
        print 'on_save:'
        print self
        if self.editfile:
            filename = self.editfile
        else:
            #current_name = _('新建文档')
            #current_name = ''
            current_name = get_doctitle(html)
            filename = gtkdialogs.save(title=_('Save'), 
                    name_mimes={_("Html Document"):"text/html"},
                    current_name=current_name,)
            if filename and not '.' in os.path.basename(filename):
                filename = filename + '.html'
        if filename:
            self.edit.lastDir = os.path.dirname(filename)
            #html = self.edit.get_html()
            if not self.editfile: self.add_recent(filename) #添加到最近文件
            file(filename, 'w').write(html)
            self.editfile = filename
            self.window.set_title(os.path.basename(self.editfile) + ' - ' + Title) 
            pass
        gtk.gdk.threads_leave()
        pass

    def on_save_as(self, *args):
        print 'on_save_as:'
        self.edit.do_html_saveas()
        pass

    def on_html_saveas(self, html):
        print 'on_save_as:'
        filename = gtkdialogs.save(title=_('SaveAS'), name_mimes={_("Html Document"):"text/html"})
        #current_name = _('新建文档')
        #current_name = ''
        current_name = get_doctitle(html)
        filename = gtkdialogs.save(title=_('Save As'), 
                name_mimes={_("Html Document"):"text/html"},
                current_name=current_name, folder=self.edit.lastDir,)
        if filename and not '.' in os.path.basename(filename):
            filename = filename + '.html'
        if filename:
            self.add_recent(filename) #添加到最近文件
            self.edit.lastDir = os.path.dirname(filename)
            #html = self.edit.get_html()
            file(filename, 'w').write(html)
            pass
        gtk.gdk.threads_leave()
        pass

    def on_print(self, *args):
        print 'on_print:'
        self.edit.do_print()
        pass

    def do_undo(self, *args):
        print 'do_undo:'
        self.window.present()
        self.edit.do_undo()
        pass

    def do_redo(self, *args):
        print 'do_redo:'
        self.window.present()
        self.edit.do_redo()
        pass

    def do_cut(self, *args):
        print 'do_cut:'
        self.window.present()
        self.edit.do_cut()
        pass

    def do_copy(self, *args):
        print 'do_copy:'
        self.window.present()
        self.edit.do_copy()
        pass

    def do_paste(self, *args):
        print 'do_paste:'
        self.window.present()
        self.edit.do_paste()
        pass

    def do_delete(self, *args):
        print 'do_delete:'
        self.window.present()
        self.edit.do_delete()
        pass

    def do_selectall(self, *args):
        print 'do_selectall:'
        self.window.present()
        self.edit.do_selectall()
        pass

    def show_findbar(self, *args):
        print 'show_findbar:'
        self.findbar.show_all()
        self.entry_searchtext.grab_focus()
        self.do_find_text()
        pass

    def view_update_contents(self, *args):
        print 'view_update_contents:'
        self.window.present()
        self.edit.do_view_update_contents()
        pass

    def view_toggle_autonumber(self, *args):
        print 'view_toggle_autonumber:'
        self.window.present()
        self.edit.do_view_toggle_autonumber()
        pass

    def view_sourceview(self, *args):
        print 'view_sourceview:'
        self.window.present()
        self.edit.do_html_view()
        #self.edit.do_bodyhtml_view()
        pass

    def do_update_images(self, *args):
        print 'do_update_images:'
        self.window.present()
        self.edit.do_image_base64()
        pass

    def do_insertimage(self, *args):
        print 'do_insertimage:'
        src = gtkdialogs.open(title=_('InsertImage'), name_mimes={_("Image Files"):"image/*"})
        if src:
            self.edit.do_insertimage(src)
        pass

    def do_createlink(self, *args):
        print 'do_createlink:'
        ##print self.edit.get_link_message()
        link = gtkdialogs.inputbox(title=_('Create Link'), label=_('URL:'), text="http://")
        if link and link != "http://":
            self.edit.do_createlink(link)
        pass

    def do_inserthorizontalrule(self, *args):
        print 'do_inserthorizontalrule:'
        self.window.present()
        self.edit.do_inserthorizontalrule()
        pass

    def do_insert_table(self, *args):
        print 'do_insert_table:'
        cow,row = gtkdialogs.spinbox2(title=_('Insert Table'),label1=_('Rows:'),value1=3, label2=_('Cows:'),value2=3)
        self.edit.do_insert_table(cow, row)
        pass

    def do_inserthtml(self, *args):
        print 'do_inserthtml:'
        html = gtkdialogs.textbox(title=_('Insert Html'), text='')
        if html:
            self.edit.do_inserthtml(html)
        pass

    def do_insert_contents(self, *args):
        print 'do_insert_contents:'
        self.window.present()
        self.edit.do_insert_contents()
        pass

    def do_formatblock_p(self, *args):
        print 'do_formatblock_p:'
        self.window.present()
        self.edit.do_formatblock_p()
        pass

    def do_formatblock_h1(self, *args):
        print 'do_formatblock_h1:'
        self.window.present()
        self.edit.do_formatblock_h1()
        pass

    def do_formatblock_h2(self, *args):
        print 'do_formatblock_h2:'
        self.window.present()
        self.edit.do_formatblock_h2()
        pass

    def do_formatblock_h3(self, *args):
        print 'do_formatblock_h3:'
        self.window.present()
        self.edit.do_formatblock_h3()
        pass

    def do_formatblock_h4(self, *args):
        print 'do_formatblock_h4:'
        self.window.present()
        self.edit.do_formatblock_h4()
        pass

    def do_formatblock_h5(self, *args):
        print 'do_formatblock_h5:'
        self.window.present()
        self.edit.do_formatblock_h5()
        pass

    def do_formatblock_h6(self, *args):
        print 'do_formatblock_h6:'
        self.window.present()
        self.edit.do_formatblock_h6()
        pass

    def do_insertunorderedlist(self, *args):
        print 'do_insertunorderedlist:'
        self.window.present()
        self.edit.do_insertunorderedlist()
        pass

    def do_insertorderedlist(self, *args):
        print 'do_insertorderedlist:'
        self.window.present()
        self.edit.do_insertorderedlist()
        pass

    def do_formatblock_address(self, *args):
        print 'do_formatblock_address:'
        self.window.present()
        self.edit.do_formatblock_address()
        pass

    def do_formatblock_code(self, *args):
        print 'do_formatblock_code:'
        self.window.present()
        self.edit.do_formatblock_code()
        pass

    def do_formatblock_blockquote(self, *args):
        print 'do_formatblock_blockquote:'
        self.window.present()
        self.edit.do_formatblock_blockquote()
        pass

    def do_formatblock_pre(self, *args):
        print 'do_formatblock_pre:'
        self.window.present()
        self.edit.do_formatblock_pre()
        pass

    def on_bold(self, *args):
        print 'on_bold:'
        self.window.present()
        self.edit.do_bold()
        pass

    def do_underline(self, *args):
        print 'do_underline:'
        self.window.present()
        self.edit.do_underline()
        pass

    def do_italic(self, *args):
        print 'do_italic:'
        self.window.present()
        self.edit.do_italic()
        pass

    def do_strikethrough(self, *args):
        print 'do_strikethrough:'
        self.window.present()
        self.edit.do_strikethrough()
        pass

    def do_font_fontname(self, widget, fontname):
        print 'do_font_fontname:', fontname
        self.window.present()
        self.edit.do_font_fontname(fontname)
        pass

    def do_fontsize_1(self, *args):
        print 'do_fontsize_1:'
        self.window.present()
        self.edit.do_fontsize_11()
        pass

    def do_fontsize_2(self, *args):
        print 'do_fontsize_2:'
        self.window.present()
        self.edit.do_fontsize_2()
        pass

    def do_fontsize_3(self, *args):
        print 'do_fontsize_3:'
        self.window.present()
        self.edit.do_fontsize_3()
        pass

    def do_fontsize_4(self, *args):
        print 'do_fontsize_4:'
        self.window.present()
        self.edit.do_fontsize_4()
        pass

    def do_fontsize_5(self, *args):
        print 'do_fontsize_5:'
        self.window.present()
        self.edit.do_fontsize_5()
        pass

    def do_fontsize_6(self, *args):
        print 'do_fontsize_6:'
        self.window.present()
        self.edit.do_fontsize_6()
        pass

    def do_fontsize_7(self, *args):
        print 'do_fontsize_7:'
        self.window.present()
        self.edit.do_fontsize_7()
        pass

    def on_color_select_forecolor(self, *args):
        print 'on_color_select_forecolor:'
        color = gtkdialogs.colorbox()
        if color:
            self.forecolor = color
            self.edit.do_color_forecolor (color)
            pass
        pass

    def do_color_hilitecolor(self, *args):
        print 'do_color_hilitecolor:'
        if "hilitecolor" in self.__dict__:
            self.edit.grab_focus()
            self.edit.do_color_hilitecolor(self.hilitecolor)
            pass
        else:
            self.on_color_select_hilitecolor()
            pass
        pass

    def on_color_select_hilitecolor(self, *args):
        print 'on_color_select_hilitecolor:'
        color = gtkdialogs.colorbox()
        if color:
            self.hilitecolor = color
            self.edit.do_color_hilitecolor(color)
        pass

    def do_removeformat(self, *args):
        print 'do_removeformat:'
        self.window.present()
        self.edit.do_removeformat()
        pass

    def do_justifyleft(self, *args):
        print 'do_justifyleft:'
        self.window.present()
        self.edit.do_justifyleft()
        pass

    def do_justifycenter(self, *args):
        print 'do_justifycenter:'
        self.window.present()
        self.edit.do_justifycenter()
        pass

    def do_justifyright(self, *args):
        print 'do_justifyright:'
        self.window.present()
        self.edit.do_justifyright()
        pass

    def do_indent(self, *args):
        print 'do_indent:'
        self.window.present()
        self.edit.do_indent()
        pass

    def do_outdent(self, *args):
        print 'do_outdent:'
        self.edit.do_outdent()
        pass

    def do_subscript(self, *args):
        print 'do_subscript:'
        self.window.present()
        self.edit.do_subscript()
        pass

    def do_superscript(self, *args):
        print 'do_superscript:'
        self.window.present()
        self.edit.do_superscript()
        pass

    def on_about(self, *args):
        print 'on_about:'
        authors = [
            "Jiahua Huang <jhuangjiahua(at)gmail.com>",
            ]
        about = gobject.new(gtk.AboutDialog, 
                name=_("RTEdit"), 
                program_name=_("RTEdit"),
                logo_icon_name="gtk-dnd",
                version="0.1", 
                copyright=_("(C) hiweed.com"),
                comments=_("Rich Text Editor"),
                license="LGPLv3",
                website="http://www.hiweed.com/",
                website_label="hiweed.com",
                authors=authors)
        #about.set_transient_for(self.window)
        about.run()     
        about.destroy()
        pass

    def hide_findbar(self, *args):
        print 'hide_findbar:'
        self.findbar.hide()
        pass

    def do_find_text_forward(self, *args):
        print 'do_find_text_forward:'
        text = self.entry_searchtext.get_text()
        if not text: return
        self.edit.do_find_text_forward(text)
        pass

    def do_find_text(self, *args):
        print 'do_find_text:'
        text = self.entry_searchtext.get_text()
        if text:
            self.edit.do_find_text(text)
        pass

    def do_replace_text(self, *args):
        print 'do_replace_text:'
        ffindtext   = self.entry_searchtext.get_text()
        replacetext = self.entry_replace_text.get_text()
        if ffindtext:
            self.edit.do_replace_text(ffindtext, replacetext)
        pass

    def do_replace_text_all(self, *args):
        print 'do_replace_text_all:'
        ffindtext   = self.entry_searchtext.get_text()
        replacetext = self.entry_replace_text.get_text()
        if ffindtext:
            self.edit.do_replace_text_all(ffindtext, replacetext)
        pass

    def get_custom_widget(self, id, string1, string2, int1, int2):
        w = gtk.Label(_("(custom widget: %s)") % id)
        return w


##cmd test

usage = _('''RTEdit

Usage:
  gedit [OPTION...] [FILE...] - Edit html files

Options:
  -h, --help                     Show help options
  -v, --version                  Show version information
''')

def openwindow(*args, **kwargs):
    '''MainWindow() 的包装
    要 return False 以免 gtk.idle_add, gtk.timeout_add 重复执行
    '''
    apply(MainWindow, args, kwargs)
    return False

def _listen(s):
    '''监听 unix socket
    '''
    print 'listen:', s
    while 1:
        conn, addr = s.accept()
        rev = conn.recv(102400)
        for i in rev.split('\n'):
            print 'Open:', i
            gobject.idle_add(openwindow, i)
            pass
        pass
    pass

def main():
    '''处理命令行
    '''
    import os, sys
    import socket
    ## 处理命令行参数
    import getopt
    gtk.gdk.threads_init()
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'vh', ['version', 'help'])
        pass
    except:
        print usage
        return
    for o, v in opts:
        if o in ('-h', '--help'):
            print usage
            return
        elif o in ('-v', '--version'):
            print __version__
            return
        pass
    ## 要 打开的文件
    editfiles = [ os.path.abspath(i) for i in args ]
    ## 设 profdir 和 ctlfile
    profdir = os.environ['HOME'] + '/.config/RTEdit'
    if not os.path.isdir(profdir): os.makedirs(profdir)    
    ## 单实例运行， 尝试用已打开 RTEdit
    ctlfile = profdir + '/rtedit.ctl'
    try:
        ## 已打开 RTEdit 的情况
        s = socket.socket(socket.AF_UNIX)
        s.connect(ctlfile)
        s.send('\n'.join(editfiles))
        print 'sent:', editfiles
        return
    except:
        #raise
        print 'new:'
        pass
    ## 监听 socket
    s = socket.socket(socket.AF_UNIX)
    if os.access(ctlfile, os.R_OK): os.remove(ctlfile)
    s.bind(ctlfile)
    s.listen(1)
    thread.start_new_thread(_listen, (s,))
    ## 打开文件
    for i in editfiles:
        i = os.path.abspath(i)
        MainWindow(editfile=i)
        pass
    if not Windows:
        MainWindow()   
        pass
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()

if __name__ == '__main__':
    main()

