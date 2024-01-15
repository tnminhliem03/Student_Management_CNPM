function change_password(user_id){
    if(confirm("Xác nhận thay đổi mật khẩu?")){
        oldPw = document.getElementById("oldPassword").value
        newPw = document.getElementById("newPassword").value
        confPw =document.getElementById("confirmPassword").value
        console.log(oldPw, newPw, confPw)
        if (oldPassword == "" || newPw == "" || confPw == ""){
            alert("Vui lòng nhập đầy đủ thông tin")
            return
            }
        else if(newPw != confPw){
            alert("Mật khẩu mới không trùng khớp")
            return
            }
        else fetch(`/api/change_password/${user_id}`,{
            method: "POST",
            body: JSON.stringify({
                "old": oldPw,
                "new": newPw
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(data => alert(data.message))
    }
}

function onFileSelected(event) {
  var selectedFile = event.target.files[0];
  var reader = new FileReader();

  var imgtag = document.getElementById("image");
  imgtag.title = selectedFile.name;

  reader.onload = function(event) {
    imgtag.src = event.target.result;
  };

  reader.readAsDataURL(selectedFile);
}