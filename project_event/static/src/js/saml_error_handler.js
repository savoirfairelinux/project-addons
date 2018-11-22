odoo.define('project_event.login_alert_message_saml', function (require) {
    "use strict";


function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}

switch(getUrlVars()["saml_error"]){
    case "1":
        $("#password").after("<br/><p class='alert alert-danger' >Il n'est pas autorisé de s'inscrire sur cette base de donnée.</p>");
        break;
    case "2":
        $("#password").after("<br/><p class='alert alert-danger' >Accès interdit.</p>");
        break;
    case "3":
        $("#password").after("<br/><p class='alert alert-danger' >Vous n'avez pas accès à cette base de donnée ou votre invitation a expirée. Veuillez demander une invitation et assurez vous de cliquer sur le lien dans l'email.</p>");
        break;
    default:
}

});
