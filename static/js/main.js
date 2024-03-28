window.onload = function () {
    loadclasses();
    loadChapter();
}
function loadclasses() {
    var classDropdown = document.getElementsByName('class_id');
    for (var i = 0; i < classDropdown.length; i++) {
        classDropdown[i].innerHTML = '';
    }
    fetch('/class')
        .then(response => response.json())
        .then(data => {
            data.forEach(class_ => {
                for (var i = 0; i < classDropdown.length; i++) {
                    var option = document.createElement('option');
                    option.value = class_.id;
                    var classId = document.getElementById('class_show').dataset.classId;
                    if (class_.id == classId) {
                        option.selected = true;
                    }
                    option.textContent = class_.name;
                    classDropdown[i].appendChild(option);
                }
            });
        })
        .catch(error => console.error('Error:', error));
}
function loadChapter() {
    var class_id = document.getElementsByName('class_id')[1].value;
    if (class_id == '') {
        class_id = document.getElementById('class_show').dataset.classId;
    }
    console.log(class_id);
    var chapterDropdown = document.getElementById('chapter_id');
    chapterDropdown.innerHTML = '';

    fetch('/chapter?class_id=' + class_id, { method: 'GET' })
        .then(response => response.json())
        .then(data => {

            data.forEach(chapter => {
                var option = document.createElement('option');
                option.value = chapter.id;
                option.textContent = chapter.name;
                if (chapter.id == document.getElementById('chapter_show').dataset.classId) {
                    option.selected = true;
                }
                chapterDropdown.appendChild(option);

            });
        })
        .catch(error => console.error('Error:', error));
}

