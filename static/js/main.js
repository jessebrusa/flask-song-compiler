function createConfirmationDialog(message, endpoint, elementId) {
    var confirmContainer = document.createElement('div');
    var textConfirm = document.createElement('h1');
    var linkContainer = document.createElement('div');
    var link1 = document.createElement('a');
    var link2 = document.createElement('button');

    confirmContainer.id = 'confirmContainer';

    textConfirm.textContent = message;
    textConfirm.style.color = 'white';

    linkContainer.className = 'linkContainer';

    let baseUrl = 'http://127.0.0.1:5001/';
    link1.href = baseUrl + endpoint;
    link1.textContent = 'YES';
    link1.className = 'removeYes';

    link2.textContent = 'NO';
    link2.className = 'removeNo';

    confirmContainer.appendChild(textConfirm);
    confirmContainer.appendChild(linkContainer);
    linkContainer.appendChild(link1);
    linkContainer.appendChild(link2);

    document.body.appendChild(confirmContainer);

    var element = document.getElementById(elementId);
    element.addEventListener('click', function () {
        removeConfirmationDialog();
    });

    link2.addEventListener('click', function () {
        removeConfirmationDialog();
    });

    function removeConfirmationDialog() {
        if (confirmContainer) {
            confirmContainer.remove();
        }
    }
}