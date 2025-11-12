function copyUrl() {
    const urlBox = document.getElementById("shortUrl");
    urlBox.select();
    document.execCommand("copy");
    alert("Copied: " + urlBox.value);
}
