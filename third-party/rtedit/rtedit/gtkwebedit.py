#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# Author: Huang Jiahua <jhuangjiahua@gmail.com>
# License: GNU LGPL
# Last modified:

"""
"""
__revision__ = '0.1'

import gtk, gobject
import gtkmozembed
import urllib2
import os, errno
import re

try: import i18n
except: import gettext.gettext as _

def stastr(stri):
    '''处理字符串的  '   "
    '''
    return stri.replace("\\","\\\\").replace(r'"',r'\"').replace(r"'",r"\'").replace('\n',r'\n')

def textbox(title='Text Box', label='Text',
        parent=None, text=''):
    """display a text edit dialog
    
    return the text , or None
    """
    dlg = gtk.Dialog(title, parent, gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OK, gtk.RESPONSE_OK    ))
    dlg.set_default_size(500,500)
    #lbl = gtk.Label(label)
    #lbl.set_alignment(0, 0.5)
    #lbl.show()
    #dlg.vbox.pack_start(lbl,  False)
    gscw = gtk.ScrolledWindow()
    #gscw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    gscw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    textview=gtk.TextView(buffer=None)
    buffer = textview.get_buffer()
    
    if text:buffer.set_text(text)    
    
    #textview.show()
    gscw.add(textview)
    #gscw.show()
    dlg.vbox.pack_start(gscw)
    dlg.show_all()
    resp = dlg.run()
    
    text=buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())
    dlg.destroy()
    if resp == gtk.RESPONSE_OK:
        return text
    return None

BLANKHTML='''<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="generator" content="RTEdit">
  <title></title>
  <style>
img{
    border: 2px;
    border-style: solid;
    border-color: #c3d9ff;
    padding: 5px;
}
h1{
    background-color:#CCFFCC;
}
h2{
    background-color:#CCFFCC;
}
h3{
    background-color:#CCFFCC;
}
h4{
    background-color:#CCFFCC;
}
h5{
    background-color:#CCFFCC;
}
h6{
    background-color:#CCFFCC;
}
blockquote{
    background-color:#EEFFFF;
    border-left: 5px solid green;
    padding-left: 5px;
    margin: 15px;
    padding: 5px;
}
pre{
    background-color:#EEEEFF;
    display: block;
    border: 1px solid green;
    margin: 15px;
    padding: 5px;
}
code{
    background-color:#EEEEFF;
    display: block;
    border: 1px solid blue;
    margin: 15px;
    padding: 5px;
}
  </style>
</head>
<body>
</body>
</html>
'''

USERJS = '''
pref("capability.policy.default.Clipboard.cutcopy", "allAccess");
pref("capability.policy.default.Clipboard.paste", "allAccess");
pref("signed.applets.codebase_principal_support", true);
pref("capability.principal.codebase.p0.granted", "UniversalBrowserRead");
pref("capability.principal.codebase.p0.id", "file://");
pref("capability.principal.codebase.p0.subjectName", "");
pref("capability.principal.codebase.p1.granted", "UniversalBrowserRead");
pref("capability.principal.codebase.p1.id", "http://127.0.0.1");
pref("capability.principal.codebase.p1.subjectName", "");
pref("capability.principal.codebase.p2.granted", "UniversalBrowserRead");
pref("capability.principal.codebase.p2.id", "moz-safe-about:blank");
pref("capability.principal.codebase.p2.subjectName", "");
pref("capability.principal.codebase.p3.granted", "UniversalBrowserRead");
pref("capability.principal.codebase.p3.id", "http://www.google.com");
pref("capability.principal.codebase.p3.subjectName", "");
pref("network.cookie.prefsMigrated", true);
pref("signed.applets.codebase_principal_support", true);
'''

class WebEdit(gtkmozembed.MozEmbed):
    '''Html Edit Widget
    '''
    def __init__(self, editfile=''):
        '''WebEdit.__init__
        '''
        profdir = os.environ['HOME'] + '/.config/GtkWebEdit'
        editdir = profdir + '/editor/'
        blankfile = profdir + '/blank.html'
        try:
            os.makedirs(editdir)
        except OSError, err:
            if err.errno != errno.EEXIST or not os.path.isdir(editdir):
                raise
        ## 允许剪贴板，允许 XMLHttpRequest 跨域请求
        file(editdir+'user.js', 'w').write(USERJS)
        if os.path.isfile(editdir+'/lock'): os.remove(editdir+'/lock')
        ##
        file(blankfile, 'w').write(BLANKHTML)
        gtkmozembed.set_profile_path(profdir, 'editor')
        gtkmozembed.MozEmbed.__init__(self)
        ##
        #self.load_url('about:blank')
        if editfile and os.access(editfile, os.R_OK):
            self.load_url(editfile)
            pass
        else:
            #self.write_html(BLANKHTML)
            self.load_url(blankfile)
            #self.load_url("about:blank")
            pass
        self.connect('title', self._on_title)
        self.connect('net-stop', self.set_editable)
        ##
        ## contextmenu ####################################
        self.contextmenu = gtk.Menu()
        self.contextmenu_undo1 = gtk.ImageMenuItem(_("gtk-undo"))
        self.contextmenu_undo1.show()
        self.contextmenu_undo1.connect("activate", self.do_undo)
        ##
        self.contextmenu.append(self.contextmenu_undo1)
        ##
        self.contextmenu_redo1 = gtk.ImageMenuItem(_("gtk-redo"))
        self.contextmenu_redo1.show()
        self.contextmenu_redo1.connect("activate", self.do_redo)
        ##
        self.contextmenu.append(self.contextmenu_redo1)
        ##
        self.contextmenu_separator1 = gtk.MenuItem()
        self.contextmenu_separator1.show()
        ##
        self.contextmenu.append(self.contextmenu_separator1)
        ##
        self.contextmenu_cut1 = gtk.ImageMenuItem(_("gtk-cut"))
        self.contextmenu_cut1.show()
        self.contextmenu_cut1.connect("activate", self.do_cut)
        ##
        self.contextmenu.append(self.contextmenu_cut1)
        ##
        self.contextmenu_copy1 = gtk.ImageMenuItem(_("gtk-copy"))
        self.contextmenu_copy1.show()
        self.contextmenu_copy1.connect("activate", self.do_copy)
        ##
        self.contextmenu.append(self.contextmenu_copy1)
        ##
        self.contextmenu_paste1 = gtk.ImageMenuItem(_("gtk-paste"))
        self.contextmenu_paste1.show()
        self.contextmenu_paste1.connect("activate", self.do_paste)
        ##
        self.contextmenu.append(self.contextmenu_paste1)
        ##
        self.contextmenu_delete1 = gtk.ImageMenuItem(_("gtk-delete"))
        self.contextmenu_delete1.show()
        self.contextmenu_delete1.connect("activate", self.do_delete)
        ##
        self.contextmenu.append(self.contextmenu_delete1)
        ##
        self.contextmenu_separator2 = gtk.MenuItem()
        self.contextmenu_separator2.show()
        ##
        self.contextmenu.append(self.contextmenu_separator2)
        ##
        self.contextmenu_selectall1 = gtk.ImageMenuItem(_("gtk-select-all"))
        self.contextmenu_selectall1.show()
        self.contextmenu_selectall1.connect("activate", self.do_selectall)
        ##
        self.contextmenu.append(self.contextmenu_selectall1)
        self.contextmenu.show_all()

    def _on_title(self, *args):
        '''monitor title
        '''
        title = self.get_title()
        #print title
        if title.startswith('_s#popup-menu:'):
            self.on_popup_menu()
            pass
        elif title.startswith('_s#html_view:'):
            self.on_html_view(title[len('_s#html_view:'):])
            pass
        elif title.startswith('_s#bodyhtml_view:'):
            self.on_bodyhtml_view(title[len('_s#bodyhtml_view:'):])
            pass
        elif title.startswith('_s#html_save:'):
            self.on_html_save(title[len('_s#html_save:'):])
            pass
        elif title.startswith('_s#bodyhtml_save:'):
            self.on_bodyhtml_save(title[len('_s#html_save:'):])
            pass
        elif title.startswith('_s#html_saveas:'):
            self.on_html_saveas(title[len('_s#html_saveas:'):])
            pass
        elif title.startswith('_s#bodyhtml_saveas:'):
            self.on_bodyhtml_saveas(title[len('_s#bodyhtml_saveas:'):])
            pass
        pass

    def write_html(self, html):
        #print 'WebEdit.write_html:'
        self.load_url(r'''javascript: 
                document.open();
                document.write("%s");
                document.close();
                void 0'''%stastr(html))
        pass

    def update_html(self, html):
        #@NOTE: 修改 documentElement.innerHTML 后无法正常编辑，改为分别更新 body 和 head
        #print 'WebEdit.update_html:'
        head = (re.findall(r'''<head>([^\0]*)</head>''', html)+[""])[0]
        body =  re.sub(r'''<head>[^\0]*</head>''', '', html)
        self.load_url(r'''javascript: 
                document.body.innerHTML="%s";
                document.getElementsByTagName("head")[0].innerHTML="%s";
                void 0'''% (stastr(body), stastr(head)))
        pass

    def update_bodyhtml(self, html):
        #print 'WebEdit.update_bodyhtml:'
        self.load_url(r'''javascript: 
                document.body.innerHTML="%s";
                void 0'''%stastr(html))
        pass

    def set_editable(self, *args):
        '''set editable
        '''
        #@TODO: 加入更新标题，更新目录 js 函数
        #print 'WebEdit.set_editable:'
        #cmd = r'''javascript: document.documentElement.contentEditable="true"; void 0'''
        cmd = r'''javascript: 
            document.documentElement.contentEditable="true";
            /*document.body.contentEditable="true";*/
            document.execCommand("useCSS",false, true);
            window.oncontextmenu=function(){document.title="_s#popup-menu:";} ;
            /* 处理标题 */
            function guesstitle(){
              if( (t=document.getElementsByTagName("title")) && (title=t[0].textContent) ){
                return title;
              }else if( (h1=document.getElementsByTagName("h1")) && h1.length>0 ){
                title=h1[0].textContent;
              } else {
                p = document.createElement('pre');
                p.innerHTML = document.body.innerHTML.replace(/</g, '\n\n<').replace(/>/g, '>\n\n');
                title = p.textContent.replace(/^\s+/g, '').split('\n')[0];
              }
              if(! document.getElementsByTagName("title") ){
                t = document.createElement('title');
                t.textContent=title;
                document.getElementsByTagName("head")[0].appendChild(t);
              }else{
                document.getElementsByTagName("title")[0].textContent=title;
              }
            };

            /* 目录处理 */
            function getheads(){
                /* 取得所有 heading 标签到 heads */
                tags = document.getElementsByTagName("*");
                heads = new Array();
                for (var i=0; i<tags.length; i++){
                    t = tags[i].nodeName;
                    if (t == "H1" || t == "H2" || t == "H3" || t == "H4" || 
                            t == "H5" || t == "H6"){
                        heads.push(tags[i]);
                    }
                }
                return heads;
            };
            
            autonu = 0;
            if( i = document.body.getAttribute("orderedheadings")){
                autonu = i;
            }
            /*@TODO: 需要将是否自动标题编号保存在 html */
            
            function toggledirnu(){
                if (autonu){
                    autonu = 0;
                    document.body.setAttribute("orderedheadings", 0);
                }else{
                    autonu = 1;
                    document.body.setAttribute("orderedheadings", 1);
                }
                updatedir();
            };
            function getiname(tt, name){
                if (autonu){
                    return tt + '  ' + iname;
                }else{
                    return iname;
                }
            }
            
            function getdir(){
                heads = getheads();
                tt = '';
                tdir = '';
                h1 = 0;
                h2 = 0;
                h3 = 0;
                h4 = 0;
                h5 = 0;
                h6 = 0;
                startHeader = 0;
                startHeader = 1;
                
                for (var i=startHeader ; i<heads.length; i++){
                    inode = heads[i];
                    iname = inode.textContent.replace(/^\s*[.\d]*\s+/, ''); /*把标题前边的数字识别为序号*/
                    iname = iname.replace('\n',' ');
                    switch(heads[i].nodeName){
                        case "H1":
                        tt = '';
                        h1 += 1;
                        h2 = 0;
                        h3 = 0;
                        h4 = 0;
                        h5 = 0;
                        h6 = 0;
                        tt += String(h1);
                        inode.id = tt;
                        inode.textContent = getiname(tt, name);   
                        tdir += '';
                        tdir += '<a href="#' + tt + '">' + getiname(tt, name) + '</a>\n';
                        break;
            
                        case "H2":
                        tt = '';
                        h2 += 1;
                        h3 = 0;
                        h4 = 0;
                        h5 = 0;
                        h6 = 0;
                        tt += String(h1) + '.' + h2;
                        inode.id = tt;
                        inode.textContent = getiname(tt, name);           
                        tdir += ' ';
                        tdir += '<a href="#' + tt + '">' + getiname(tt, name) + '</a>\n';
                        break;
            
                        case "H3":
                        tt = '';
                        h3 += 1;
                        h4 = 0;
                        h5 = 0;
                        h6 = 0;
                        tt += String(h1) + '.' + h2 + '.' + h3;
                        inode.id = tt;
                        inode.textContent = getiname(tt, name);           
                        tdir += '  ';
                        tdir += '<a href="#' + tt + '">' + getiname(tt, name) + '</a>\n';
                        break;
            
                        case "H4":
                        tt = '';
                        h4 += 1;
                        h5 = 0;
                        h6 = 0;
                        tt += String(h1) + '.' + h2 + '.' + h3 + '.' +h4;
                        inode.id = tt;
                        inode.textContent = getiname(tt, name);           
                        tdir += '   ';
                        tdir += '<a href="#' + tt + '">' + getiname(tt, name) + '</a>\n';
                        break;
            
                        case "H5":
                        tt = '';
                        h5 += 1;
                        h6 = 0;
                        tt += String(h1) + '.' + h2 + '.' + h3 + '.' + h4 + '.' + h5;
                        inode.id = tt;
                        inode.textContent = getiname(tt, name);           
                        tdir += '    ';
                        tdir += '<a href="#' + tt + '">' + getiname(tt, name) + '</a>\n';
                        break;
            
                        case "H6":
                        tt = '';
                        h6 += 1;
                        tt += String(h1) + '.' + h2 + '.' + h3 + '.' + h4 + '.' + h5 + '.' + h6;
                        inode.id = tt;
                        inode.textContent = getiname(tt, name);           
                        tdir += '     ';
                        tdir += '<a href="#' + tt + '">' + getiname(tt, name) + '</a>\n';
                        break;
                    }
            
                }
                pre = document.createElement('pre');
                pre.innerHTML = tdir;
                tdir = pre.innerHTML;
                document.title = tdir;
                return tdir;
            }
            
            function updatedir(){
                dirhtml = getdir();
                if (t=document.getElementById("toctitledir")){
                    t.innerHTML = dirhtml;
                }
            };
                        
            void 0;'''
        self.load_url(cmd)
        pass

    def do_image_base64(self, *args):
        '''convert images to base64 inline image
        see http://tools.ietf.org/html/rfc2397
        '''
        #print 'WebEdit.convert images to base64 inline image'
        self.load_url(r'''javascript:
        var keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
        function encode64(input) {
           var output = "";
           var chr1, chr2, chr3;
           var enc1, enc2, enc3, enc4;
           var i = 0;
           do {
              chr1 = input.charCodeAt(i++) & 0xff;
              chr2 = input.charCodeAt(i++) & 0xff;
              chr3 = input.charCodeAt(i++) & 0xff;
              enc1 = chr1 >> 2;
              enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
              enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
              enc4 = chr3 & 63;
              if (isNaN(chr2)) {
                 enc3 = enc4 = 64;
              } else if (isNaN(chr3)) {
                 enc4 = 64;
              }
              output = output + keyStr.charAt(enc1) + keyStr.charAt(enc2) + 
                 keyStr.charAt(enc3) + keyStr.charAt(enc4);
           } while (i < input.length);   
           return output;
        };
        netscape.security.PrivilegeManager.enablePrivilege("UniversalBrowserRead");      
        for (var i=document.images.length-1; i+1; i--){
             img = document.images[i];
             if(img.src && !img.src.match(/^data:/)){
                 mx = new XMLHttpRequest();
                 mx.open("GET", img.src, false);
                 mx.overrideMimeType('text/plain; charset=x-user-defined');           
                 mx.send(null);
                 if (mx.responseText && (mx.status==200 || mx.status==0) ){
                     img.setAttribute('uri', img.src);
                     img.src = "data:image;base64," + encode64(mx.responseText);
                 };
             }
        };
        void 0;
        ''')
        pass

    def on_popup_menu(self, *args):
        #print 'WebEdit.on_popup_menu:'
        if self.emit('popup-menu'): 
            return
        self.contextmenu.popup(None, None, None, 0, 0)
        pass


    def do_html_view(self, *args):
        #print 'WebEdit.do_html_view:'
        self.do_image_base64()
        gobject.timeout_add(100, self.load_url, r'''javascript: 
            updatedir();
            document.title = '_s#html_view:<html>'+document.documentElement.innerHTML+'</html>'; void 0''')
        pass

    def do_bodyhtml_view(self, *args):
        #print 'WebEdit.do_bodyhtml_view:'
        self.do_image_base64()
        gobject.timeout_add(100, self.load_url, r'''javascript: 
            updatedir();
            document.title = '_s#bodyhtml_view:'+document.body.innerHTML; void 0''')
        pass


    def do_html_save(self, *args):
        #print 'WebEdit.do_html_save'
        self.do_image_base64()
        gobject.timeout_add(100, self.load_url, r'''javascript: 
            guesstitle();
            updatedir();
            document.title = '_s#html_save:<html>\n'+document.documentElement.innerHTML+'\n</html>'; void 0''')
        pass

    def do_html_saveas(self, *args):
        #print 'WebEdit.do_html_view'
        self.do_image_base64()
        gobject.timeout_add(100, self.load_url, r'''javascript: 
            guesstitle();
            updatedir();
            document.title = '_s#html_save:<html>\n'+document.documentElement.innerHTML+'\n</html>'; void 0''')
        pass

    def on_html_view(self, html):
        '''on html view
        '''
        #print 'WebEdit.on_html_view:'
        gtk.gdk.threads_enter()
        html = textbox(title=_("HTML"), text=html)
        if html:
            gobject.timeout_add(100, self.update_html,html)
            pass
        gtk.gdk.threads_leave()
        pass

    def on_bodyhtml_view(self, html):
        '''on bodyhtml view
        '''
        #print 'WebEdit.on_bodyhtml_view:'
        gtk.gdk.threads_enter()        
        html = textbox(title=_("HTML"), text=html)
        if html:
            gobject.timeout_add(100, self.update_bodyhtml, html)
            pass
        gtk.gdk.threads_leave()
        pass

    def on_html_save(self, html):
        '''on html save
        '''
        #print html
        pass

    def on_html_saveas(self, html):
        '''on html save as
        '''
        #print html
        pass

    def on_bodyhtml_save(self, bodyhtml):
        '''on bodyhtml save
        '''
        #print bodyhtml
        pass

    def on_bodyhtml_saveas(self, bodyhtml):
        '''on bodyhtml save
        '''
        #print bodyhtml
        pass

    def do_print(self, *args):
        #print 'WebEdit.do_print:'
        self.load_url('javascript: print(); void 0')
        pass

    def do_undo(self, *args):
        #print 'WebEdit.do_undo:'
        self.load_url('javascript: document.execCommand("undo", false, false); void 0')

    def do_redo(self, *args):
        #print 'WebEdit.do_redo:'
        self.load_url('javascript: document.execCommand("redo", false, false); void 0')

    def do_cut(self, *args):
        #print 'WebEdit.do_cut:'
        self.load_url('javascript: document.execCommand("cut", false, false); void 0')

    def do_copy(self, *args):
        #print 'WebEdit.do_copy:'
        self.load_url('javascript: document.execCommand("copy", false, false); void 0')

    def do_paste(self, *args):
        #print 'WebEdit.do_paste:'
        self.load_url('javascript: document.execCommand("paste", false, false); void 0')

    def do_delete(self, *args):
        #print 'WebEdit.do_delete:'
        self.load_url('javascript: document.execCommand("delete", false, false); void 0')

    def do_selectall(self, *args):
        #print 'WebEdit.do_selectall:'
        self.load_url('javascript: document.execCommand("selectall", false, false); void 0')

    ################################################
    #
    def do_view_update_contents(self, *args):
        #print 'WebEdit.view_update_contents:'
        self.load_url(r'''javascript:
            updatedir();
            void 0''')
        pass

    def do_view_toggle_autonumber(self, *args):
        #print 'WebEdit.view_toggle_autonumber:'
        self.load_url(r'''javascript:
            toggledirnu();
            void 0''')
        pass

    def do_view_sourceview(self, *args):
        #print 'WebEdit.view_sourceview:'
        self.do_html_view()
        pass

    def do_insertimage(self, img=""):
        #print 'WebEdit.do_insertimage:'
        self.load_url('''javascript: 
                document.execCommand("insertimage", false, "%s"); 
                void 0'''%stastr(img))
        pass

    def do_createlink(self, link=""):
        #print 'WebEdit.do_createlink:'
        self.load_url(r'''javascript: 
                link = "%s";
                if( document.getSelection() ){
                    document.execCommand("createlink", false, link); 
                }else{
                    text = link;
                    i = document.createElement("div");
                    i.textContent = text;
                    text = i.innerHTML;
                    html = '<a href="' + link + '">' + text + '</a>';
                    document.execCommand("inserthtml", false, html);
                }
                void 0'''%stastr(link))
        pass

    def do_inserthorizontalrule(self, *args):
        #print 'WebEdit.do_inserthorizontalrule:'
        self.load_url('''javascript: 
                document.execCommand("inserthorizontalrule", false, false); void 0''')
        pass

    def do_insert_table(self, rows, cows):
        #print 'WebEdit.do_insert_table:'
        html = "\n<table border='2px' width='100%' ><tbody>\n"
        for row in range(int(rows)):
            html+= "<tr>\n"
            for cow in range(int(cows)):
                html+= "        <td> </td>\n"
            html+= "</tr>\n"
        html+= "</tbody></table>\n"
        self.do_inserthtml(html)
        pass

    def do_inserthtml(self, html):
        #print 'WebEdit.do_inserthtml:'
        self.load_url('''javascript: 
                document.execCommand("inserthtml", false, "%s"); 
                void 0'''%stastr(html))
        pass

    def do_insert_contents(self, *args):
        #print 'WebEdit.do_insert_contents:'
        #@FIXME: 无法删除现存目录表格
        self.load_url(r'''javascript: 
            if(t=document.getElementById("toctitle")){
                document.removeChild(t);
            }
            html = '<pre id="toctitle" contentEditable="false" style="background-color:#EEEEFF; display: block; border: 1px solid green; margin: 15px; padding: 5px;"><div title="点击固定目录" onclick=\' t = document.getElementById("toctitle"); if(this.alt){ this.alt = 0; document.body.style.cssText=" "; t.style.cssText=" "; }else{ this.alt = 1; document.body.style.cssText="margin:5pt; border:5pt; height:100%; width:70%; overflow-y:auto;"; t.style.cssText="display:block; top:10px; right:0; width:25%; height:90%; overflow:auto; position:fixed;"; } \' class="dirtitle">目录:<br/></div><span id="toctitledir"> </span></pre>'; 
            document.execCommand("inserthtml", false, html); 
            updatedir();
            void 0''')
        pass

    def do_formatblock_p(self, *args):
        #print 'WebEdit.do_formatblock_p:'
        self.load_url('''javascript: 
                document.execCommand("formatblock", false, "p"); 
                updatedir();
                void 0''')
        pass

    def do_formatblock_h1(self, *args):
        #print 'WebEdit.do_formatblock_h1:'
        self.load_url('''javascript: 
                document.execCommand("formatblock", false, "h1"); 
                updatedir();
                void 0''')
        pass

    def do_formatblock_h2(self, *args):
        #print 'WebEdit.do_formatblock_h2:'
        self.load_url('''javascript: 
                document.execCommand("formatblock", false, "h2"); 
                updatedir();
                void 0''')
        pass

    def do_formatblock_h3(self, *args):
        #print 'WebEdit.do_formatblock_h3:'
        self.load_url('''javascript: 
                document.execCommand("formatblock", false, "h3");
                updatedir();
void 0''')
        pass

    def do_formatblock_h4(self, *args):
        #print 'WebEdit.do_formatblock_h4:'
        self.load_url('''javascript: 
                document.execCommand("formatblock", false, "h4");
                updatedir();
                void 0''')
        pass

    def do_formatblock_h5(self, *args):
        #print 'WebEdit.do_formatblock_h5:'
        self.load_url('''javascript: 
                document.execCommand("formatblock", false, "h5");
                updatedir();
                void 0''')
        pass

    def do_formatblock_h6(self, *args):
        #print 'WebEdit.do_formatblock_h6:'
        self.load_url('''javascript: 
                document.execCommand("formatblock", false, "h6");
                updatedir();
                void 0''')
        pass

    def do_insertunorderedlist(self, *args):
        #print 'WebEdit.do_insertunorderedlist:'
        self.load_url('''javascript: 
                document.execCommand("insertunorderedlist", false, null); void 0''')
        pass

    def do_insertorderedlist(self, *args):
        #print 'WebEdit.do_insertorderedlist:'
        self.load_url('''javascript: 
                document.execCommand("insertorderedlist", false, null); void 0''')
        pass

    def do_formatblock_address(self, *args):
        #print 'WebEdit.formatblock_addres:'
        self.load_url('''javascript: 
                document.execCommand("formatblock", false, "address"); void 0''')
        pass

    def do_formatblock_code(self, *args):
        #print 'WebEdit.do_formatblock_code:'
        #@FIXME: formatblock code 无效
        self.load_url('''javascript: 
                document.execCommand("formatblock", false, "code"); void 0''')
        pass

    def do_formatblock_blockquote(self, *args):
        #print 'WebEdit.do_formatblock_blockquote:'
        self.load_url('''javascript: 
                document.execCommand("formatblock", false, "blockquote"); void 0''')
        pass

    def do_formatblock_pre(self, *args):
        #print 'WebEdit.do_do_formatblock_pre:'
        self.load_url('''javascript: 
                document.execCommand("formatblock", false, "pre"); void 0''')
        pass

    def do_bold(self, *args):
        #print 'WebEdit.do_bold:'
        self.load_url('''javascript: 
                document.execCommand("bold", false, null); void 0''')
        pass

    def do_underline(self, *args):
        #print 'WebEdit.do_underline:'
        self.load_url('''javascript: 
                document.execCommand("underline", false, null); void 0''')
        pass

    def do_italic(self, *args):
        #print 'WebEdit.do_italic:'
        self.load_url('''javascript: 
                document.execCommand("italic", false, null); void 0''')
        pass

    def do_strikethrough(self, *args):
        #print 'WebEdit.do_strikethrough:'
        self.load_url('''javascript: 
                document.execCommand("strikethrough", false, null); void 0''')
        pass

    def do_font_fontname(self, fontname):
        #print 'WebEdit.do_font_fontname:'
        self.load_url(r'''javascript: 
                document.execCommand("fontname", false, "%s"); 
                void 0'''%fontname)
        pass

    def do_fontsize(self, fontsize):
        #print 'WebEdit.do_fontsize:'
        self.load_url(r'''javascript: 
                document.execCommand("fontsize", false, "%s"); 
                void 0'''%fontsize)
        pass

    def do_fontsize_1(self, *args):
        #print 'WebEdit.do_fontsize_1:'
        self.do_fontsize(1)
        pass

    def do_fontsize_2(self, *args):
        #print 'WebEdit.do_fontsize_2:'
        self.do_fontsize(2)
        pass

    def do_fontsize_3(self, *args):
        #print 'WebEdit.do_fontsize_3:'
        self.do_fontsize(3)
        pass

    def do_fontsize_4(self, *args):
        #print 'WebEdit.do_fontsize_4:'
        self.do_fontsize(4)
        pass

    def do_fontsize_5(self, *args):
        #print 'WebEdit.do_fontsize_5:'
        self.do_fontsize(5)
        pass

    def do_fontsize_6(self, *args):
        #print 'WebEdit.do_fontsize_6:'
        self.do_fontsize(6)
        pass

    def do_fontsize_7(self, *args):
        #print 'WebEdit.do_fontsize_7:'
        self.do_fontsize(7)
        pass

    def do_color_forecolor(self, color):
        #print 'WebEdit.do_color_forecolor:'
        self.load_url(r'''javascript: 
                document.execCommand("useCSS",false, false);
                document.execCommand("foreColor", false, "%s"); 
                document.execCommand("useCSS",false, true);
                void 0'''%color)
        pass

    def do_color_hilitecolor(self, color):
        # 设背景色无效 需要 useCSS 选项 
        #print 'WebEdit.do_color_hilitecolor:'
        self.load_url(r'''javascript: 
                document.execCommand("useCSS",false, false);
                document.execCommand("hilitecolor", false, "%s"); 
                document.execCommand("useCSS",false, true);
                void 0'''%color)
        pass

    def do_removeformat(self, *args):
        #print 'WebEdit.do_removeformat:'
        self.load_url('''javascript: 
                document.execCommand("removeformat", false, null); void 0''')
        pass

    def do_justifyleft(self, *args):
        #print 'WebEdit.do_justifyleft:'
        self.load_url('''javascript: 
                document.execCommand("justifyleft", false, null); void 0''')
        pass

    def do_justifycenter(self, *args):
        #print 'WebEdit.do_justifycenter:'
        self.load_url('''javascript: 
                document.execCommand("justifycenter", false, null); void 0''')
        pass

    def do_justifyright(self, *args):
        #print 'WebEdit.do_justifyright:'
        self.load_url('''javascript: 
                document.execCommand("justifyright", false, null); void 0''')
        pass

    def do_indent(self, *args):
        #print 'WebEdit.do_indent:'
        self.load_url('''javascript: 
                document.execCommand("indent", false, null); void 0''')
        pass

    def do_outdent(self, *args):
        #print 'WebEdit.do_outdent:'
        self.load_url('''javascript: 
                document.execCommand("outdent", false, null); void 0''')
        pass

    def do_subscript(self, *args):
        #print 'WebEdit.do_subscript:'
        self.load_url('''javascript: 
                document.execCommand("subscript", false, null); void 0''')
        pass

    def do_superscript(self, *args):
        #print 'WebEdit.do_subperscript:'
        self.load_url('''javascript: 
                document.execCommand("superscript", false, null); void 0''')
        pass

    ##
    def do_find_text(self, findtext, caseSensitive="false", backwards="false" ,
            wrapAround="true" , wholeWord="false" , searchInFrames="true" ,
            showDialog="false" ):
        '''find ( String str , 
                  boolean caseSensitive , 
                  boolean backwards , 
                  boolean wrapAround , 
                  boolean wholeWord , 
                  boolean searchInFrames , 
                  boolean showDialog )
        '''
        #print 'WebEdit.do_find_text:', findtext, backwards
        cmd = '''javascript:
                window.find("%s", %s, %s, %s, %s, %s, %s);
                void 0'''%(stastr(findtext),
                           caseSensitive,
                           backwards,
                           wrapAround,
                           wholeWord,
                           searchInFrames,
                           showDialog,)
        self.load_url(cmd)
        pass

    def do_find_text_forward(self, findtext):
        '''find text, forward
        wind.find(String, false, true, true, true, true, false)
        '''
        #print 'WebEdit.do_find_text_forward:', findtext,
        self.do_find_text(findtext, backwards="true")
        pass

    def do_replace_text(self, findtext, replacetext):
        #print 'WebEdit.do_replace_text:'
        self.load_url('''javascript:
                if( document.getSelection() ){
                    var text = "%s";
                    var i = document.createElement("div");
                    i.textContent = text;
                    text = i.innerHTML;
                    document.execCommand("inserthtml", false, text);
                };
                window.find("%s", false, false, true, true, true, false); 
                void 0'''%(stastr(replacetext),stastr(findtext)) )
        pass  

    def do_replace_text_all(self, findtext, replacetext):
        '''全部替换
        '''
        #print 'WebEdit.do_replace_text_all'
        self.load_url('''javascript:
                var findtext = "%s";
                var i = 0;
                while(window.find(findtext, false, true, false, true, true, false)){
                  i = 1;
                } /* 临时用来到页首 */
                while( i || window.find(findtext, false, false, false, true, true, false) ){
                    i=0;
                    if( document.getSelection() ){
                        text = "%s";
                        i = document.createElement("div");
                        i.textContent = text;
                        text = i.innerHTML;
                        document.execCommand("inserthtml", false, text);
                    }
                }; void 0'''%(stastr(findtext),stastr(replacetext)) )
        pass

    


if __name__=="__main__":
    #print 'WebEdit.main'
    w=gtk.Window()
    w.connect("delete_event", gtk.main_quit)
    m=WebEdit()
    w.add(m)
    w.show_all()
    gtk.main()



