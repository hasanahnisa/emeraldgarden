function tampilkanFasilitas() {
    $("#daftar-fasilitas").empty();

    $.ajax({
      type: "GET",
      url: `/get_fasilitas`, // Gunakan backtick (`) untuk template literals
      success: function (response) {
        if (response && response.fasilitas) {
          let fasilitas = response.fasilitas;

          // Loop melalui fasilitas dan membuat kartu fasilitas secara dinamis
          for (let i = 0; i < fasilitas.length; i++) {
            let namaFasilitas = fasilitas[i].nama;
            let jenisFasilitas = fasilitas[i].jenis;
            let deskripsiFasilitas = fasilitas[i].deskripsi;
            let gambarFasilitas = fasilitas[i].gambar;

            let kartuFasilitas = `
          <div class="col">
          <div class="card shadow-sm">
          <img
          src="../static/${gambarFasilitas}"
          class="card-img-top"
          alt="Gambar Fasilitas"
          style="object-fit: cover; height: 200px;"
        />
            <div class="col">
              <div class="card-body">
                <b>${namaFasilitas}</b><br />
                <b>${jenisFasilitas}</b><br />
                <p class="card-text">
                  ${deskripsiFasilitas}
                </p>
              </div>
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
  