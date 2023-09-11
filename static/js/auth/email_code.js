$(document).ready(function() {
    $('#email-button').click((e) => {
        e.preventDefault();
        let code_type = $('#code-type').val();
        let email = $('#email').val();
        if (!email) {
            alert('Please enter an email address');
            return;
        }
        let url = code_type === "recovery" ? "/api/v1/auth/recovery" : "/api/v1/auth/activate";
        $.ajax({
            url: url,
            type: "POST",
            data: JSON.stringify({email: email}),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                let content = $(".email-code-content");
                let link_for = code_type === "recovery"? "recovery" : "activation";
                let article = code_type === "recovery"? "A" : "An";
                content.html(`
                <p>${article} ${link_for} link to your account has been sent to your email. Please check it.</p>
                <a href="/auth/login/" class="btn btn-primary">Log in</a>
                `)
            },
            error: function(data) {
                alert(data.responseJSON.detail)
            }
        });
    });
});
