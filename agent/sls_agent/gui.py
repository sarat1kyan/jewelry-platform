def toast(message: str):
    try:
        from winrt.windows.ui.notifications import ToastNotificationManager, ToastTemplateType
        from winrt.windows.data.xml.dom import XmlDocument
        ttype = ToastTemplateType.TOAST_TEXT02
        xml = ToastNotificationManager.get_template_content(ttype)
        texts = xml.get_elements_by_tag_name("text")
        texts.item(0).append_child(xml.create_text_node("SLS Agent"))
        texts.item(1).append_child(xml.create_text_node(message))
        notifier = ToastNotificationManager.create_toast_notifier("SLS Agent")
        from winrt.windows.ui.notifications import ToastNotification
        notifier.show(ToastNotification(xml))
    except Exception:
        print("[toast]", message)
