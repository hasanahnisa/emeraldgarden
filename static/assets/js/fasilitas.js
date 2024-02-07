function tampilkanFasilitas() {
    $("#daftar-fasilitas").empty();

    $.ajax({
      type: "GET",
      url: `/get_fasilitas`, 
      success: function (response) {
        if (response && response.fasilitas) {
          let fasilitas = response.fasilitas;

          // Loop melalui fasilitas dan membuat kartu fasilitas secara dinamis
          for (let i = 0; i < fasilitas.length; i++) {
            let namaFasilitas = fasilitas[i].nama;
            let deskripsiFasilitas = fasilitas[i].deskripsi;
            let gambarFasilitas = fasilitas[i].gambar;

            let kartuFasilitas = `
            <div style="display: flex; margin-bottom: 20px; border-bottom: 1px solid #ccc; padding-bottom: 20px;">
  <div class="row">
    <img
      src="../static/${gambarFasilitas}"
      class="img-top"
      alt="Gambar Fasilitas"
      style="object-fit: cover; height: 200px; flex: 1; margin-right: 20px;"
    />
    <div class="body" style="flex: 2;">
      <b>${namaFasilitas}</b><br />
      <p class="text">
        ${deskripsiFasilitas}
      </p>
    </div>
  </div>
</div>



        `;

            $("#daftar-fasilitas").append(kartuFasilitas);
          }
        } else {
          console.error("Format respons server tidak sesuai.");
        }
      },
      error: function (error) {
        console.error("Error mengambil data fasilitas:", error);
      },
    });
  }
  