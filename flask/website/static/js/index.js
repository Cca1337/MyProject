function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/notes";
  });
}

function deletePic(picId) {
  fetch("/delete-picture", {
    method: "POST",
    body: JSON.stringify({ picId: picId }),
  }).then((_res) => {
    window.location.href = "/obrazky_update";
  });
}

$(document).ready(function() {
  setTimeout(function() {
    $("#proceed").show();
  }, 21000);
});