(function($) {
    $(document).ready(function() {
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
        {shoe_sizes} - <b>размеры обуви (для офферов)</b>
    </p>
</div>
        `);

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
            $("textarea#id_text").val(drafts[value]);
        });

        setInterval(function() {
            var amountOfButtons = Number($("select#id_amount_of_buttons").val());
            for(var buttonNumber = 1; buttonNumber <= amountOfButtons; buttonNumber++) {
                $(".form-row.field-button_" + buttonNumber + "_title.field-button_" + buttonNumber + "_link").show();
            }
            for(var buttonNumber = amountOfButtons + 1; buttonNumber <= 4; buttonNumber++) {
                $(".form-row.field-button_" + buttonNumber + "_title.field-button_" + buttonNumber + "_link").hide();
            }
        }, 10);

        $('form').submit(function() {
            if($("input[name=_save]").val() == "Выложить") {
                var confirmation = confirm("Выложить пост?");
                return confirmation;
            } else {
                return true;
            }
        });

        setInterval(function() {
            if($("input#id_post_all").prop("checked")) {
                $(".field-post_need_spam_setup, .field-post_0_referrals, .field-post_1_referrals, .field-post_2_referrals, .field-post_3_and_more_referrals").hide();
            } else {
                $(".field-post_need_spam_setup, .field-post_0_referrals, .field-post_1_referrals, .field-post_2_referrals, .field-post_3_and_more_referrals").show();
            }
        }, 10);

        setInterval(function() {
            var gender = $("select#id_offer_gender").val();
            if(gender == "male") {
                var minSize = 38;
                var maxSize = 47;
            } else if(gender == "female") {
                var minSize = 36;
                var maxSize = 43;
            } else {
                var minSize = 36;
                var maxSize = 47;
            }
            for(var size = 36; size < minSize; size++) {
                $(".field-offer_size_" + size + ", .field-offer_size_" + size + "_5").hide();
            }
            for(var size = minSize; size <= maxSize; size++) {
                $(".field-offer_size_" + size + ", .field-offer_size_" + size + "_5").show();
            }
            for(var size = maxSize + 1; size <= 47; size++) {
                $(".field-offer_size_" + size + ", .field-offer_size_" + size + "_5").hide();
            }
        }, 10);

        setInterval(function () {
            if(!$(".deletelink").length && !$(".closelink").length) {
                var postponedPostType = $("select#id_type").val();

                var
                    postForm = $("#postponedpost_form fieldset:nth-of-type(3)"),
                    offerForm = $("#postponedpost_form fieldset:nth-of-type(4)");

                var draftInput = $(".form-row.field-draft");

                if(postponedPostType == "post") {
                    postForm.show();
                    offerForm.hide();
                    draftInput.hide();
                } else if (postponedPostType == "offer") {
                    postForm.hide();
                    offerForm.show();
                    draftInput.show();
                } else {
                    postForm.hide();
                    offerForm.hide();
                    draftInput.hide();
                }
            }
        }, 10);

        setInterval(function () {
            var postpone = $("input#id_postpone").prop("checked");

            var postponeTime = $(".form-row.field-postpone_time");
            var saveButton = $("input[name=_save]");

            if(postpone) {
                postponeTime.show();
                saveButton.val("Отложить");
            } else {
                postponeTime.hide();
                saveButton.val("Выложить");
            }
        }, 10);
    });
})(django.jQuery);
