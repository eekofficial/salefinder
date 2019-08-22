(function($) {
    $(document).ready(function() {
        if(window.location.href.includes("change")) {
            $("#content").prepend(`
<div style="margin-bottom: 20px; padding-top: 10px; padding-bottom: 5px; padding-left: 10px; padding-right: 10px; background: rgb(245, 245, 245);">
    <p><b>Доступные html теги:</b></p>
    <p>
        &lt;b&gt;bold&lt;/b&gt;, &lt;strong&gt;bold&lt;/strong&gt; - <b>жирный текст</b></br>
        &lt;i&gt;italic&lt;/i&gt;, &lt;em&gt;italic&lt;/em&gt; - <b>курсив</b></br>
        &lt;a href="http://www.example.com/"&gt;inline URL&lt;/a&gt; - <b>ссылка</b></br>
        &lt;a href="tg://user?id=123456789"&gt;inline mention of a user&lt;/a&gt; - <b>упоминание пользователя</b>
    </p>
    <p style="display: block; margin-top: 20px;"><b>Специальные вставки:</b></p>
    <p>
        {user} - <b>имя пользователя (не ник)</b>
    </p>
</div>
            `);

            $("input[name=_save]").hide();
            $("input[name=_continue]").val("Отправить сообщение/изменить состояние");

            var draftsString = String($("fieldset .description").html());
            var draftsArray = draftsString.split("__secret_delimiter__");
            var drafts = [];
            for(var i = 0; i < draftsArray.length; i++) {
                var draft = String(draftsArray[i]).split("__secret_inner_delimiter__");
                drafts[Number(draft[0])] = draft[1];
            }
            $("select#id_draft").change(function() {
                var value = Number($(this).val());
                console.log(value);
                $("textarea#id_message").val(drafts[value]);
            });

            $("fieldset.module.aligned:nth-of-type(2) .form-row").hide();
            $("fieldset.module.aligned:nth-of-type(2)").append("<div class='dialog'>" + $("#id_data").val() + "</div>");
        }
    });
})(django.jQuery);
