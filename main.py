from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Input, Button, Select, Static, DataTable, Label
from textual.binding import Binding

# Daftar Status PTKP default sesuai peraturan perpajakan Indonesia
PTKP_OPTIONS = [
    ("TK/0 - Rp 54.000.000", 54_000_000),
    ("TK/1 - Rp 58.500.000", 58_500_000),
    ("TK/2 - Rp 63.000.000", 63_000_000),
    ("TK/3 - Rp 67.500.000", 67_500_000),
    ("K/0  - Rp 58.500.000", 58_500_000),
    ("K/1  - Rp 63.000.000", 63_000_000),
    ("K/2  - Rp 67.500.000", 67_500_000),
    ("K/3  - Rp 72.000.000", 72_000_000),
]

def hitung_pph21_custom(pkp: float, custom_layers: list):
    """
    Menghitung rincian PPh 21 progresif berdasarkan lapisan dan tarif 
    yang diinput sendiri oleh pengguna.
    custom_layers berisi list tuple: (batas_atas, persentase_tarif, label_deskripsi)
    """
    sisa_pkp = pkp
    total_pajak = 0.0
    rincian = []

    for batas, tarif, label in custom_layers:
        if sisa_pkp <= 0:
            break
        kena_pajak = min(sisa_pkp, batas)
        pajak_lapisan = kena_pajak * (tarif / 100.0) # Konversi persen ke desimal
        total_pajak += pajak_lapisan
        rincian.append((label, f"Rp {kena_pajak:,.0f}", f"{tarif}%", f"Rp {pajak_lapisan:,.0f}"))
        sisa_pkp -= kena_pajak

    return total_pajak, rincian


class CustomTaxCalculatorApp(App):
    """Aplikasi Kalkulator Pajak PPh 21 dengan Tarif Kustom Interaktif."""

    TITLE = "KALKULATOR PAJAK PPh 21 - CUSTOM TARIF"
    SUB_TITLE = "Input penghasilan dan atur tarif pajak sendiri"
    
    CSS = """
    Screen {
        background: #0f172a;
        color: #f8fafc;
    }

    #main-container {
        layout: horizontal;
        padding: 1 2;
        height: 100%;
    }

    #left-panel {
        width: 45%;
        background: #1e293b;
        border: tall #38bdf8;
        padding: 1 2;
        margin-right: 1;
    }

    #right-panel {
        width: 55%;
        background: #1e293b;
        border: tall #10b981;
        padding: 1 2;
    }

    .section-title {
        text-style: bold;
        color: #38bdf8;
        margin-bottom: 1;
        border-bottom: solid #334155;
        padding-bottom: 1;
    }

    .section-title-green {
        text-style: bold;
        color: #10b981;
        margin-bottom: 1;
        border-bottom: solid #334155;
        padding-bottom: 1;
    }

    Label {
        margin-top: 1;
        color: #cbd5e1;
    }

    Input {
        margin-bottom: 1;
        background: #0f172a;
        border: tall #475569;
    }

    Input:focus {
        border: tall #38bdf8;
    }

    Select {
        margin-bottom: 1;
    }

    #button-group {
        layout: horizontal;
        height: auto;
        margin-top: 1;
    }

    Button {
        width: 1fr;
        margin-right: 1;
    }

    #btn-reset {
        margin-right: 0;
    }

    #error-msg {
        color: #f87171;
        text-style: bold;
        margin-top: 1;
        height: auto;
    }

    #summary-box {
        background: #0f172a;
        padding: 1 2;
        border: round #334155;
        margin-bottom: 1;
        height: auto;
    }

    DataTable {
        height: 1fr;
        background: #0f172a;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Keluar", show=True),
        Binding("ctrl+r", "reset_form", "Reset", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            # PANEL KIRI: FORM INPUT PENGHASILAN & TARIF KUSTOM
            with ScrollableContainer(id="left-panel"):
                yield Static("📥 INPUT DATA & TARIF PAJAK", classes="section-title")
                
                yield Label("Gaji Bersih per Bulan (IDR):")
                yield Input(placeholder="Contoh: 10000000", id="input-gaji", type="number")
                
                yield Label("Bonus / THR Tahunan (IDR):")
                yield Input(placeholder="Contoh: 15000000 (Kosongkan jika 0)", id="input-bonus", type="number")
                
                yield Label("Status PTKP:")
                yield Select(PTKP_OPTIONS, value=54_000_000, id="select-ptkp")

                yield Label("Atur Lapisan Tarif Sendiri (Format: Batas Atas, Tarif %):")
                yield Label("• Lapisan 1 (Maksimal s.d. Nilai & Tarif %):")
                with Horizontal():
                    yield Input(placeholder="Batas (Cth: 60000000)", id="l1-batas", value="60000000")
                    yield Input(placeholder="Tarif % (Cth: 5)", id="l1-tarif", value="5")

                yield Label("• Lapisan 2 (Maksimal s.d. Nilai selisih & Tarif %):")
                with Horizontal():
                    yield Input(placeholder="Batas (Cth: 190000000)", id="l2-batas", value="190000000")
                    yield Input(placeholder="Tarif % (Cth: 15)", id="l2-tarif", value="15")

                yield Label("• Lapisan 3 (Seterusnya / Tanpa Batas Akhir):")
                with Horizontal():
                    yield Input(placeholder="Tarif Sisa PKP % (Cth: 25)", id="l3-tarif", value="25")
                
                with Horizontal(id="button-group"):
                    yield Button("🧮 Hitung Pajak", variant="primary", id="btn-hitung")
                    yield Button("🔄 Reset", variant="error", id="btn-reset")
                
                yield Static("", id="error-msg")

            # PANEL KANAN: HASIL PERHITUNGAN
            with Vertical(id="right-panel"):
                yield Static("📊 LAPORAN PERHITUNGAN CUSTOM", classes="section-title-green")
                
                yield Static(
                    "Silakan isi data gaji dan atur tarif kustom di sebelah kiri, lalu klik [b]Hitung Pajak[/b].",
                    id="summary-box"
                )
                
                yield Label("Rincian Lapisan Tarif Kustom:")
                yield DataTable(id="tabel-rincian")

        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#tabel-rincian", DataTable)
        table.add_columns("Lapisan Tarif", "Dasar Kena Pajak", "Tarif", "Pajak Terhutang")
        table.cursor_type = "row"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-hitung":
            self.proses_kalkulasi()
        elif event.button.id == "btn-reset":
            self.action_reset_form()

    def action_reset_form(self) -> None:
        self.query_one("#input-gaji", Input).value = ""
        self.query_one("#input-bonus", Input).value = ""
        self.query_one("#select-ptkp", Select).value = 54_000_000
        self.query_one("#l1-batas", Input).value = "60000000"
        self.query_one("#l1-tarif", Input).value = "5"
        self.query_one("#l2-batas", Input).value = "190000000"
        self.query_one("#l2-tarif", Input).value = "15"
        self.query_one("#l3-tarif", Input).value = "25"
        self.query_one("#error-msg", Static).update("")
        self.query_one("#summary-box", Static).update("Form telah direset.")
        self.query_one("#tabel-rincian", DataTable).clear()

    def proses_kalkulasi(self) -> None:
        error_label = self.query_one("#error-msg", Static)
        summary_box = self.query_one("#summary-box", Static)
        table = self.query_one("#tabel-rincian", DataTable)

        raw_gaji = self.query_one("#input-gaji", Input).value.strip()
        raw_bonus = self.query_one("#input-bonus", Input).value.strip()
        ptkp = self.query_one("#select-ptkp", Select).value

        if not raw_gaji:
            error_label.update("⚠️ Error: Gaji bulanan wajib diisi!")
            return

        try:
            gaji_bulanan = float(raw_gaji)
            bonus_tahunan = float(raw_bonus) if raw_bonus else 0.0

            l1_b = float(self.query_one("#l1-batas", Input).value)
            l1_t = float(self.query_one("#l1-tarif", Input).value)
            l2_b = float(self.query_one("#l2-batas", Input).value)
            l2_t = float(self.query_one("#l2-tarif", Input).value)
            l3_t = float(self.query_one("#l3-tarif", Input).value)

            if gaji_bulanan < 0 or bonus_tahunan < 0:
                error_label.update("⚠️ Error: Nominal tidak boleh negatif!")
                return
        except ValueError:
            error_label.update("⚠️ Error: Pastikan semua input angka diisi dengan benar!")
            return

        error_label.update("")

        # Menyusun lapisan kustom
        custom_layers = [
            (l1_b, l1_t, f"Lapisan 1 (s.d. Rp {l1_b:,.0f})"),
            (l2_b, l2_t, f"Lapisan 2 (s.d. Rp {l2_b:,.0f})"),
            (float('inf'), l3_t, "Lapisan 3 (Sisa PKP berikutnya)")
        ]

        bruto_tahun = (gaji_bulanan * 12) + bonus_tahunan
        biaya_jabatan = min(0.05 * bruto_tahun, 6_000_000)
        neto_tahun = bruto_tahun - biaya_jabatan
        pkp = max(0.0, neto_tahun - float(ptkp))

        total_pajak_tahun, rincian = hitung_pph21_custom(pkp, custom_layers)
        pajak_bulan = total_pajak_tahun / 12

        laporan_text = (
            f"• Penghasilan Bruto Setahun : Rp {bruto_tahun:,.0f}\n"
            f"• Biaya Jabatan             : Rp {biaya_jabatan:,.0f}\n"
            f"• Penghasilan Neto Setahun  : Rp {neto_tahun:,.0f}\n"
            f"• PTKP Sesuai Status        : Rp {ptkp:,.0f}\n"
            f"• Penghasilan Kena Pajak    : [b cyan]Rp {pkp:,.0f}[/b cyan]\n"
            f"──────────────────────────────────────────────────\n"
            f"💰 [b green]TOTAL PAJAK / TAHUN : Rp {total_pajak_tahun:,.0f}[/b green]\n"
            f"📅 [b yellow]TOTAL PAJAK / BULAN : Rp {pajak_bulan:,.0f}[/b yellow]"
        )
        summary_box.update(laporan_text)

        table.clear()
        if pkp == 0:
            table.add_row("Penghasilan di bawah PTKP (Nihil)", "Rp 0", "0%", "Rp 0")
        else:
            for row in rincian:
                table.add_row(*row)


if __name__ == "__main__":
    app = CustomTaxCalculatorApp()
    app.run()