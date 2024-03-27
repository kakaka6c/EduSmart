function loadChapter() {
    var class_id = document.getElementById('class_select')[0].value;
    if (class_id == '') {
        class_id = 1;
    }
    var chapterDropdown = document.getElementById('chapter_select');
    chapterDropdown.innerHTML = '';
    var option = document.createElement('option');
    option.value = 0;
    option.textContent = "Select Chapter";
    chapterDropdown.appendChild(option);
    fetch('/chapter?class_id=' + class_id, { method: 'GET' })
        .then(response => response.json())
        .then(data => {

            data.forEach(chapter => {
                var option = document.createElement('option');
                option.value = chapter.id;
                option.textContent = chapter.name;
                chapterDropdown.appendChild(option);
            });
        })
        .catch(error => console.error('Error:', error));
}

function loadTopics() {
    var chapter_id = document.getElementById('chapter_select').value;
    var topicDropdown = document.getElementById('topic_select');
    topicDropdown.innerHTML = '';
    fetch('/topic?chapter_id=' + chapter_id, { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            data.forEach(topic => {
                var option = document.createElement('option');
                option.value = topic.id;
                option.textContent = topic.name;
                topicDropdown.appendChild(option);
            });
        })
        .catch(error => console.error('Error:', error));
}

function ans_to_json() {
    var json_data = {
        "value1": document.getElementById("option1").value,
        "value2": document.getElementById("option2").value,
        "value3": document.getElementById("option3").value,
        "value4": document.getElementById("option4").value
    };


    var ans = JSON.stringify(json_data);
    document.getElementById("ans").value = ans;
    correct= document.getElementById("correct_option").value
    document.getElementById("correct").value = correct;
}

function add_answer() {
    // remove all select options
    var options = document.getElementsByName("correct_option");
    for (var i = 0; i < options.length; i++) {
        options[i].innerHTML = '';
    }
    // get 4 options and add to select options
    var options= document.getElementsByName("option");
    var correct= document.getElementById("correct_option");
    for (var i = 0; i < options.length; i++) {
        var option = document.createElement('option');
        option.value = options[i].value;
        option.textContent = options[i].value;
        correct.appendChild(option);
    }
    ans_to_json();


}
