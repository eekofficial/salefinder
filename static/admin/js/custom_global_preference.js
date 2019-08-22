(function($) {
    $(document).ready(function() {
        $(".breadcrumbs").html('<a href="/admin/">Начало</a> › <a href="/admin/dynamic_preferences/">Настройки</a> › Изменение текстов и цены премиума');

        $("#changelist").prepend(`
<div style="margin-bottom: 20px; padding-top: 10px; padding-bottom: 5px; background: rgb(245, 245, 245);">
    <p><b>Доступные html теги:</b></p>
    <p>
        &lt;b&gt;bold&lt;/b&gt;, &lt;strong&gt;bold&lt;/strong&gt; - <b>жирный текст</b></br>
        &lt;i&gt;italic&lt;/i&gt;, &lt;em&gt;italic&lt;/em&gt; - <b>курсив</b></br>
        &lt;a href="http://www.example.com/"&gt;inline URL&lt;/a&gt; - <b>ссылка</b></br>
        &lt;a href="tg://user?id=123456789"&gt;inline mention of a user&lt;/a&gt; - <b>упоминание пользователя</b>
    </p>
    <p style="display: block; margin-top: 20px;"><b>Специальные вставки:</b></p>
    <p>
        {number} - <b>количество рефералов в сообщении "Реферальная программа"</b>
    </p>
</div>
`);

        $(".column-verbose_name .text span").html("Название");
        $(".column-raw_value .text a").html("Значение");
        $(".column-default_value .text span").html("Значение по умолчанию");

        $(".paginator").html('<input name="_save" class="default" value="Сохранить" type="submit">');
    });
})(django.jQuery);
