from flask import Flask, render_template, request, jsonify, send_file
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import random
import datetime
import time
from database import FuzzyDatabase
from models import FuzzyCalculation, WeatherConditions, NeedLevels

app = Flask(__name__)

# Initialize database with MySQL configuration
# Sesuaikan parameter koneksi MySQL sesuai dengan setup Anda
db_manager = FuzzyDatabase(
    host="localhost",      # Host MySQL server
    database="fuzzy_irrigation",  # Nama database
    user="root",          # Username MySQL
    password="",          # Password MySQL (kosongkan jika tidak ada password)
    port=3306            # Port MySQL (default: 3306)
)

class FuzzyTsukamoto:
    def __init__(self):
        # Variabel untuk menyimpan data input dan output
        self.history = []
    
    def durasi_rendah(self, x):
        """Fungsi keanggotaan durasi rendah (0-20 detik)"""
        if x <= 5:
            return 1
        elif x <= 20:
            return (20 - x) / 15
        else:
            return 0
    
    def durasi_sedang(self, x):
        """Fungsi keanggotaan durasi sedang (10-40 detik)"""
        if x <= 10:
            return 0
        elif x <= 20:
            return (x - 10) / 10
        elif x <= 30:
            return 1
        elif x <= 40:
            return (40 - x) / 10
        else:
            return 0
    
    def durasi_tinggi(self, x):
        """Fungsi keanggotaan durasi tinggi (30-60 detik)"""
        if x <= 30:
            return 0
        elif x <= 45:
            return (x - 30) / 15
        else:
            return 1
    
    def kelembaban_rendah(self, x):
        """Fungsi keanggotaan kelembaban rendah (0-40%)"""
        if x <= 20:
            return 1
        elif 20 < x <= 40:
            return (40 - x) / 20
        else:
            return 0
    
    def kelembaban_sedang(self, x):
        """Fungsi keanggotaan kelembaban sedang (20-60%)"""
        if 20 <= x <= 40:
            return (x - 20) / 20
        elif 40 < x <= 60:
            return (60 - x) / 20
        else:
            return 0
    
    def kelembaban_tinggi(self, x):
        """Fungsi keanggotaan kelembaban tinggi (40-100%)"""
        if x <= 40:
            return 0
        elif 40 < x <= 60:
            return (x - 40) / 20
        else:
            return 1
    
    def cuaca_cerah(self, cuaca):
        """Fungsi keanggotaan cuaca cerah"""
        return 1 if cuaca == "Cerah" else 0
    
    def cuaca_berawan(self, cuaca):
        """Fungsi keanggotaan cuaca berawan"""
        return 1 if cuaca == "Berawan" else 0
    
    def cuaca_hujan_ringan(self, cuaca):
        """Fungsi keanggotaan cuaca hujan ringan"""
        return 1 if cuaca == "Hujan Ringan" else 0
    
    def cuaca_hujan_lebat(self, cuaca):
        """Fungsi keanggotaan cuaca hujan lebat"""
        return 1 if cuaca == "Hujan Lebat" else 0
    
    def hitung_durasi_penyiraman(self, kelembaban, cuaca):
        """Implementasi metode Fuzzy Tsukamoto"""
        
        # Fuzzifikasi input
        k_rendah = self.kelembaban_rendah(kelembaban)
        k_sedang = self.kelembaban_sedang(kelembaban)
        k_tinggi = self.kelembaban_tinggi(kelembaban)
        
        c_cerah = self.cuaca_cerah(cuaca)
        c_berawan = self.cuaca_berawan(cuaca)
        c_hujan_ringan = self.cuaca_hujan_ringan(cuaca)
        c_hujan_lebat = self.cuaca_hujan_lebat(cuaca)
        
        # Aturan fuzzy dan inferensi
        rules = []
        
        # Rule 1: Jika kelembaban rendah dan cuaca cerah -> penyiraman tinggi (45 detik)
        alpha1 = min(k_rendah, c_cerah)
        if alpha1 > 0:
            z1 = 45
            rules.append((alpha1, z1, "Kelembaban rendah + cuaca cerah"))
        
        # Rule 2: Jika kelembaban rendah dan cuaca berawan -> penyiraman tinggi (40 detik)
        alpha2 = min(k_rendah, c_berawan)
        if alpha2 > 0:
            z2 = 40
            rules.append((alpha2, z2, "Kelembaban rendah + cuaca berawan"))
        
        # Rule 3: Jika kelembaban rendah dan cuaca hujan ringan -> penyiraman sedang (30 detik)
        alpha3 = min(k_rendah, c_hujan_ringan)
        if alpha3 > 0:
            z3 = 30
            rules.append((alpha3, z3, "Kelembaban rendah + hujan ringan"))
        
        # Rule 4: Jika kelembaban rendah dan cuaca hujan lebat -> penyiraman rendah (15 detik)
        alpha4 = min(k_rendah, c_hujan_lebat)
        if alpha4 > 0:
            z4 = 15
            rules.append((alpha4, z4, "Kelembaban rendah + hujan lebat"))
        
        # Rule 5: Jika kelembaban sedang dan cuaca cerah -> penyiraman sedang (35 detik)
        alpha5 = min(k_sedang, c_cerah)
        if alpha5 > 0:
            z5 = 35
            rules.append((alpha5, z5, "Kelembaban sedang + cuaca cerah"))
        
        # Rule 6: Jika kelembaban sedang dan cuaca berawan -> penyiraman sedang (25 detik)
        alpha6 = min(k_sedang, c_berawan)
        if alpha6 > 0:
            z6 = 25
            rules.append((alpha6, z6, "Kelembaban sedang + cuaca berawan"))
        
        # Rule 7: Jika kelembaban sedang dan cuaca hujan ringan -> penyiraman rendah (20 detik)
        alpha7 = min(k_sedang, c_hujan_ringan)
        if alpha7 > 0:
            z7 = 20
            rules.append((alpha7, z7, "Kelembaban sedang + hujan ringan"))
        
        # Rule 8: Jika kelembaban sedang dan cuaca hujan lebat -> penyiraman rendah (10 detik)
        alpha8 = min(k_sedang, c_hujan_lebat)
        if alpha8 > 0:
            z8 = 10
            rules.append((alpha8, z8, "Kelembaban sedang + hujan lebat"))
        
        # Rule 9: Jika kelembaban tinggi dan cuaca cerah -> penyiraman rendah (15 detik)
        alpha9 = min(k_tinggi, c_cerah)
        if alpha9 > 0:
            z9 = 15
            rules.append((alpha9, z9, "Kelembaban tinggi + cuaca cerah"))
        
        # Rule 10: Jika kelembaban tinggi dan cuaca berawan -> penyiraman rendah (10 detik)
        alpha10 = min(k_tinggi, c_berawan)
        if alpha10 > 0:
            z10 = 10
            rules.append((alpha10, z10, "Kelembaban tinggi + cuaca berawan"))
        
        # Rule 11: Jika kelembaban tinggi dan cuaca hujan -> penyiraman rendah (5 detik)
        alpha11 = min(k_tinggi, c_hujan_ringan)
        if alpha11 > 0:
            z11 = 5
            rules.append((alpha11, z11, "Kelembaban tinggi + hujan ringan"))
        
        # Rule 12: Jika kelembaban tinggi dan cuaca hujan lebat -> tidak perlu penyiraman (0 detik)
        alpha12 = min(k_tinggi, c_hujan_lebat)
        if alpha12 > 0:
            z12 = 0
            rules.append((alpha12, z12, "Kelembaban tinggi + hujan lebat"))
        
        # Defuzzifikasi menggunakan metode Tsukamoto (weighted average)
        if rules:
            numerator = sum(alpha * z for alpha, z, _ in rules)
            denominator = sum(alpha for alpha, z, _ in rules)
            durasi = numerator / denominator if denominator > 0 else 0
        else:
            durasi = 0
        
        # Tentukan tingkat kebutuhan penyiraman berdasarkan durasi (dalam detik)
        if durasi <= 15:
            tingkat = "Rendah"
        elif durasi <= 35:
            tingkat = "Sedang"
        else:
            tingkat = "Tinggi"
        
        # Generate insights
        insights = self.generate_insights(kelembaban, cuaca, round(durasi, 2), tingkat, rules)
        
        # Simpan ke history
        result = {
            'kelembaban': kelembaban,
            'cuaca': cuaca,
            'durasi': round(durasi, 2),
            'tingkat': tingkat,
            'rules': rules,
            'fuzzifikasi': {
                'kelembaban_rendah': round(k_rendah, 3),
                'kelembaban_sedang': round(k_sedang, 3),
                'kelembaban_tinggi': round(k_tinggi, 3),
                'cuaca_aktif': cuaca
            },
            'insights': insights
        }
        
        self.history.append(result)
        
        return result
        
    def generate_membership_graph(self, highlight_input=None):
        """Generate membership function graph for soil moisture with optional input highlighting"""
        # Create figure with Indonesian labels
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Define x range (0-100% moisture)
        x = np.linspace(0, 100, 1000)
        
        # Calculate membership values
        rendah = [self.kelembaban_rendah(xi) for xi in x]
        sedang = [self.kelembaban_sedang(xi) for xi in x]
        tinggi = [self.kelembaban_tinggi(xi) for xi in x]
        
        # Plot membership functions with enhanced styling
        ax.plot(x, rendah, 'r-', linewidth=3, label='Rendah', alpha=0.8)
        ax.plot(x, sedang, 'g-', linewidth=3, label='Sedang', alpha=0.8) 
        ax.plot(x, tinggi, 'b-', linewidth=3, label='Tinggi', alpha=0.8)
        
        # Fill areas under curves for better visualization
        ax.fill_between(x, rendah, alpha=0.2, color='red')
        ax.fill_between(x, sedang, alpha=0.2, color='green')
        ax.fill_between(x, tinggi, alpha=0.2, color='blue')
        
        # Highlight input value if provided
        if highlight_input is not None and 0 <= highlight_input <= 100:
            # Calculate membership values for the input
            mu_rendah = self.kelembaban_rendah(highlight_input)
            mu_sedang = self.kelembaban_sedang(highlight_input)
            mu_tinggi = self.kelembaban_tinggi(highlight_input)
            
            # Draw vertical line at input value
            ax.axvline(x=highlight_input, color='black', linestyle='--', linewidth=2, alpha=0.7)
            
            # Mark membership values with dots
            ax.plot(highlight_input, mu_rendah, 'ro', markersize=8, markerfacecolor='red', markeredgecolor='darkred', markeredgewidth=2)
            ax.plot(highlight_input, mu_sedang, 'go', markersize=8, markerfacecolor='green', markeredgecolor='darkgreen', markeredgewidth=2)
            ax.plot(highlight_input, mu_tinggi, 'bo', markersize=8, markerfacecolor='blue', markeredgecolor='darkblue', markeredgewidth=2)
            
            # Add value annotations
            ax.annotate(f'μ_rendah = {mu_rendah:.3f}', 
                       xy=(highlight_input, mu_rendah), 
                       xytext=(highlight_input + 15, mu_rendah + 0.1),
                       fontsize=10, fontweight='bold', color='darkred',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='red', alpha=0.8),
                       arrowprops=dict(arrowstyle='->', color='red', alpha=0.7))
            
            ax.annotate(f'μ_sedang = {mu_sedang:.3f}', 
                       xy=(highlight_input, mu_sedang), 
                       xytext=(highlight_input + 15, mu_sedang + 0.1),
                       fontsize=10, fontweight='bold', color='darkgreen',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='green', alpha=0.8),
                       arrowprops=dict(arrowstyle='->', color='green', alpha=0.7))
            
            ax.annotate(f'μ_tinggi = {mu_tinggi:.3f}', 
                       xy=(highlight_input, mu_tinggi), 
                       xytext=(highlight_input + 15, mu_tinggi + 0.1),
                       fontsize=10, fontweight='bold', color='darkblue',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='blue', alpha=0.8),
                       arrowprops=dict(arrowstyle='->', color='blue', alpha=0.7))
            
            # Add input value label
            ax.annotate(f'Input: {highlight_input}%', 
                       xy=(highlight_input, 0), 
                       xytext=(highlight_input, -0.15),
                       fontsize=12, fontweight='bold', color='black',
                       ha='center',
                       bbox=dict(boxstyle="round,pad=0.5", facecolor='yellow', alpha=0.8))
        
        # Customize plot with enhanced styling
        ax.set_xlabel('Kelembaban Tanah (%)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Derajat Keanggotaan', fontsize=14, fontweight='bold')
        
        # Dynamic title based on whether input is highlighted
        if highlight_input is not None:
            ax.set_title(f'Fungsi Keanggotaan Kelembaban Tanah\nDengan Input Terbaru: {highlight_input}%', 
                        fontsize=16, fontweight='bold', pad=20)
        else:
            ax.set_title('Fungsi Keanggotaan Kelembaban Tanah', 
                        fontsize=16, fontweight='bold', pad=20)
        
        ax.grid(True, alpha=0.4, linestyle='-', linewidth=0.5)
        ax.legend(fontsize=12, loc='upper right', framealpha=0.9)
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.2, 1.2)
        
        # Add enhanced annotations for key transition points
        key_points = [
            (0, 'Sangat Kering'),
            (20, 'Transisi Rendah-Sedang'),
            (40, 'Optimal Sedang'),
            (60, 'Transisi Sedang-Tinggi'),
            (100, 'Sangat Basah')
        ]
        
        for point, label in key_points:
            ax.axvline(x=point, color='gray', linestyle=':', alpha=0.5)
            ax.text(point, 1.15, label, rotation=45, ha='left', va='bottom', 
                   fontsize=9, alpha=0.7, style='italic')
        
        # Add color-coded regions
        ax.axvspan(0, 20, alpha=0.1, color='red', label='_nolegend_')
        ax.axvspan(20, 60, alpha=0.1, color='green', label='_nolegend_')
        ax.axvspan(60, 100, alpha=0.1, color='blue', label='_nolegend_')
        
        plt.tight_layout()
        
        # Convert plot to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=200, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)  # Close figure to free memory
        return img_base64
    
    def generate_insights(self, kelembaban, cuaca, durasi, tingkat, rules):
        """Generate insights and recommendations based on calculation results"""
        insights = []
        recommendations = []
        
        # Analisis kondisi kelembaban
        if kelembaban <= 20:
            insights.append("🔴 Kondisi tanah sangat kering - memerlukan perhatian segera")
            recommendations.append("Lakukan penyiraman intensif dan pantau kelembaban secara berkala")
        elif kelembaban <= 40:
            insights.append("🟡 Kondisi tanah cukup kering - perlu penyiraman")
            recommendations.append("Tingkatkan frekuensi penyiraman untuk menjaga kelembaban optimal")
        elif kelembaban <= 60:
            insights.append("🟢 Kondisi kelembaban tanah dalam rentang normal")
            recommendations.append("Pertahankan jadwal penyiraman rutin sesuai kondisi cuaca")
        elif kelembaban <= 80:
            insights.append("🔵 Kondisi tanah cukup lembab - penyiraman minimal")
            recommendations.append("Kurangi intensitas penyiraman dan pastikan drainase baik")
        else:
            insights.append("🟣 Kondisi tanah sangat lembab - risiko overwatering")
            recommendations.append("Hentikan penyiraman sementara dan periksa sistem drainase")
        
        # Analisis pengaruh cuaca
        weather_impact = {
            "Cerah": {
                "icon": "☀️",
                "impact": "Cuaca cerah meningkatkan evaporasi air dari tanah",
                "advice": "Penyiraman lebih intensif diperlukan untuk mengkompensasi penguapan"
            },
            "Berawan": {
                "icon": "⛅",
                "impact": "Cuaca berawan mengurangi tingkat evaporasi",
                "advice": "Penyiraman dapat dikurangi karena penguapan lebih rendah"
            },
            "Hujan Ringan": {
                "icon": "🌦️",
                "impact": "Hujan ringan memberikan kelembaban tambahan alami",
                "advice": "Penyiraman dapat dikurangi atau ditunda sesuai intensitas hujan"
            },
            "Hujan Lebat": {
                "icon": "🌧️",
                "impact": "Hujan lebat memberikan kelembaban berlebih",
                "advice": "Hentikan penyiraman dan pastikan drainase berfungsi baik"
            }
        }
        
        if cuaca in weather_impact:
            weather_info = weather_impact[cuaca]
            insights.append(f"{weather_info['icon']} {weather_info['impact']}")
            recommendations.append(weather_info['advice'])
        
        # Analisis hasil penyiraman
        if durasi == 0:
            insights.append("✅ Tidak diperlukan penyiraman saat ini")
            recommendations.append("Pantau kondisi tanah dalam 6-12 jam ke depan")
        elif durasi <= 10:
            insights.append("💧 Penyiraman sangat ringan sudah cukup")
            recommendations.append("Lakukan penyiraman singkat dengan semprotan halus")
        elif durasi <= 25:
            insights.append("💦 Penyiraman ringan diperlukan")
            recommendations.append("Lakukan penyiraman dengan tekanan rendah")
        elif durasi <= 40:
            insights.append("🌊 Penyiraman sedang diperlukan")
            recommendations.append("Lakukan penyiraman dengan intensitas normal untuk tanaman kecil")
        else:
            insights.append("🚿 Penyiraman intensif diperlukan")
            recommendations.append("Lakukan penyiraman bertahap untuk tanaman yang sangat kering")
        
        # Analisis aturan fuzzy yang dominan
        if rules:
            dominant_rule = max(rules, key=lambda x: x[0])  # Rule dengan alpha tertinggi
            alpha_value = dominant_rule[0]
            rule_desc = dominant_rule[2]
            
            if alpha_value >= 0.8:
                insights.append(f"🎯 Keputusan sangat yakin berdasarkan: {rule_desc}")
            elif alpha_value >= 0.5:
                insights.append(f"✓ Keputusan cukup yakin berdasarkan: {rule_desc}")
            else:
                insights.append(f"⚠️ Keputusan dengan tingkat keyakinan rendah: {rule_desc}")
        
        # Rekomendasi waktu penyiraman
        if durasi > 0:
            if cuaca in ["Cerah"]:
                recommendations.append("⏰ Waktu optimal: pagi hari (06:00-08:00) atau sore hari (17:00-19:00)")
            elif cuaca in ["Berawan"]:
                recommendations.append("⏰ Waktu optimal: pagi atau siang hari (08:00-16:00)")
            else:
                recommendations.append("⏰ Hindari penyiraman saat hujan, tunggu hingga cuaca membaik")
        
        # Peringatan khusus
        warnings = []
        if kelembaban > 80 and cuaca in ["Hujan Ringan", "Hujan Lebat"]:
            warnings.append("⚠️ PERINGATAN: Risiko tinggi genangan air dan pembusukan akar")
        elif kelembaban < 20 and cuaca == "Cerah":
            warnings.append("⚠️ PERINGATAN: Risiko stress kekeringan pada tanaman")
        elif durasi > 50:
            warnings.append("⚠️ PERINGATAN: Durasi penyiraman cukup lama untuk tanaman kecil, lakukan secara bertahap")
        
        return {
            "insights": insights,
            "recommendations": recommendations,
            "warnings": warnings,
            "summary": f"Berdasarkan kelembaban {kelembaban}% dan cuaca {cuaca}, sistem merekomendasikan penyiraman {tingkat.lower()} selama {durasi} detik."
        }

# Inisialisasi fuzzy system
fuzzy_system = FuzzyTsukamoto()

# Global variable untuk menyimpan hasil perhitungan fuzzy terbaru
latest_fuzzy_result = {
    'timestamp': None,
    'kelembaban_input': None,
    'cuaca_input': None,
    'durasi_output': None,
    'tingkat_output': None,
    'is_active': False
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    global latest_fuzzy_result
    
    try:
        # Validasi input - handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            kelembaban = float(data.get('humidity', data.get('kelembaban', 0)))
            cuaca = data.get('weather', data.get('cuaca', ''))
        else:
            kelembaban = float(request.form.get('kelembaban', 0))
            cuaca = request.form.get('cuaca', '')
        
        # Validasi range kelembaban
        if not (0 <= kelembaban <= 100):
            return jsonify({
                'error': 'Kelembaban harus antara 0-100%'
            }), 400
        
        # Validasi pilihan cuaca
        cuaca_valid = ['Cerah', 'Berawan', 'Hujan Ringan', 'Hujan Lebat']
        if cuaca not in cuaca_valid:
            return jsonify({
                'error': 'Pilihan cuaca tidak valid'
            }), 400
        
        # Hitung menggunakan fuzzy logic
        result = fuzzy_system.hitung_durasi_penyiraman(kelembaban, cuaca)
        
        # Generate sensor data based on weather
        sensor_data = generate_weather_based_sensor_data(cuaca)
        
        # Simpan hasil ke global variable untuk monitoring
        latest_fuzzy_result = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'kelembaban_input': kelembaban,
            'cuaca_input': cuaca,
            'durasi_output': result['durasi'],
            'tingkat_output': result['tingkat'],
            'is_active': True
        }
        
        # Simpan ke database
        try:
            calculation_data = {
                'kelembaban_input': kelembaban,
                'cuaca_input': cuaca,
                'durasi_output': result['durasi'],
                'tingkat_kebutuhan': result['tingkat'],
                'kelembaban_tanah': sensor_data['kelembaban_tanah'],
                'suhu': sensor_data['suhu'],
                'kelembaban_udara': sensor_data['kelembaban_udara'],
                'curah_hujan': sensor_data['curah_hujan'],
                'status_pompa': "Aktif" if result['durasi'] > 0 else "Tidak Aktif",
                'timestamp': datetime.datetime.now()
            }
            
            calculation_id = db_manager.save_calculation(calculation_data)
            print(f"Calculation saved to database with ID: {calculation_id}")
            
            # Update result with database ID for reference
            result['database_id'] = calculation_id
            result['saved_to_database'] = True
            
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            result['saved_to_database'] = False
            result['database_error'] = str(db_error)
            # Continue without failing the request
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except ValueError:
        return jsonify({
            'error': 'Input kelembaban harus berupa angka'
        }), 400
    except Exception as e:
        return jsonify({
            'error': f'Terjadi kesalahan: {str(e)}'
        }), 500

@app.route('/membership_graph')
def membership_graph():
    """Generate and return membership function graph with latest calculation highlight"""
    try:
        # Get the latest calculation input for highlighting
        highlight_value = None
        if latest_fuzzy_result['is_active'] and latest_fuzzy_result['kelembaban_input'] is not None:
            highlight_value = latest_fuzzy_result['kelembaban_input']
        
        # Generate graph with or without highlighting
        graph_base64 = fuzzy_system.generate_membership_graph(highlight_input=highlight_value)
        
        return jsonify({
            'success': True,
            'graph': graph_base64,
            'highlighted_input': highlight_value,
            'calculation_data': latest_fuzzy_result if latest_fuzzy_result['is_active'] else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Gagal membuat grafik: {str(e)}'
        }), 500

@app.route('/history')
def history():
    return jsonify({
        'history': fuzzy_system.history
    })

# IoT Monitoring System Endpoints
# Monitoring functionality is now integrated into the main index page

def generate_weather_based_sensor_data(cuaca_input):
    """Generate sensor data based on weather conditions"""
    
    if cuaca_input == 'Cerah':
        # Cuaca cerah: suhu tinggi, kelembaban udara rendah, tidak ada hujan
        suhu = round(random.uniform(28, 35), 1)  # Suhu tinggi
        udara = round(random.uniform(30, 50), 1)  # Kelembaban udara rendah
        hujan = 0  # Tidak ada hujan
        
    elif cuaca_input == 'Berawan':
        # Cuaca berawan: suhu sedang, kelembaban udara sedang, hujan minimal
        suhu = round(random.uniform(24, 30), 1)  # Suhu sedang
        udara = round(random.uniform(50, 70), 1)  # Kelembaban udara sedang
        hujan = round(random.uniform(0, 2), 1)  # Hujan sangat ringan atau tidak ada
        
    elif cuaca_input == 'Hujan Ringan':
        # Hujan ringan: suhu lebih rendah, kelembaban tinggi, curah hujan ringan
        suhu = round(random.uniform(20, 26), 1)  # Suhu lebih rendah
        udara = round(random.uniform(70, 85), 1)  # Kelembaban udara tinggi
        hujan = round(random.uniform(2, 15), 1)  # Curah hujan ringan
        
    elif cuaca_input == 'Hujan Lebat':
        # Hujan lebat: suhu rendah, kelembaban sangat tinggi, curah hujan tinggi
        suhu = round(random.uniform(18, 24), 1)  # Suhu rendah
        udara = round(random.uniform(80, 95), 1)  # Kelembaban udara sangat tinggi
        hujan = round(random.uniform(15, 50), 1)  # Curah hujan lebat
        
    else:
        # Default fallback
        suhu = round(random.uniform(20, 35), 1)
        udara = round(random.uniform(40, 90), 1)
        hujan = round(random.uniform(0, 50), 1)
    
    return suhu, udara, hujan

@app.route('/api/sensor-data')
def get_sensor_data():
    """API endpoint untuk mendapatkan data sensor IoT dengan integrasi hasil fuzzy"""
    global latest_fuzzy_result
    
    current_time = datetime.datetime.now()
    
    # Jika ada hasil fuzzy yang aktif, gunakan data tersebut
    if latest_fuzzy_result['is_active']:
        # Gunakan hasil perhitungan fuzzy untuk kelembaban tanah dan durasi penyiraman
        kelembaban_tanah = latest_fuzzy_result['kelembaban_input']
        durasi_penyiraman = latest_fuzzy_result['durasi_output']
        
        # Tentukan status pompa berdasarkan durasi
        status_pompa = 'ON' if durasi_penyiraman > 0 else 'OFF'
        
        # Generate data sensor berdasarkan kondisi cuaca
        suhu, udara, hujan = generate_weather_based_sensor_data(latest_fuzzy_result['cuaca_input'])
        
        data = {
            'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'kelembaban_tanah': kelembaban_tanah,
            'suhu': suhu,
            'udara': udara,
            'hujan': hujan,
            'status_pompa': status_pompa,
            'durasi_penyiraman': durasi_penyiraman,
            'fuzzy_source': True,  # Indikator bahwa data berasal dari perhitungan fuzzy
            'cuaca_input': latest_fuzzy_result['cuaca_input'],
            'tingkat_kebutuhan': latest_fuzzy_result['tingkat_output'],
            'fuzzy_timestamp': latest_fuzzy_result['timestamp']
        }
    else:
        # Generate dummy sensor data seperti biasa
        data = {
            'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'kelembaban_tanah': round(random.uniform(20, 80), 1),
            'suhu': round(random.uniform(20, 35), 1),
            'udara': round(random.uniform(40, 90), 1),
            'hujan': round(random.uniform(0, 50), 1),
            'status_pompa': random.choice(['ON', 'OFF']),
            'durasi_penyiraman': round(random.uniform(0, 45), 1),
            'fuzzy_source': False
        }
    
    return jsonify(data)

# Database and Insights Endpoints
@app.route('/api/insights')
def get_insights():
    """API endpoint untuk mendapatkan insight dari data perhitungan fuzzy"""
    try:
        insights = db_manager.get_calculation_statistics()
        return jsonify({
            'success': True,
            'insights': insights
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Gagal mengambil insights: {str(e)}'
        }), 500

@app.route('/api/calculations')
def get_calculations():
    """API endpoint untuk mendapatkan riwayat perhitungan fuzzy"""
    try:
        limit = request.args.get('limit', 50, type=int)
        weather_filter = request.args.get('weather', None)
        
        if weather_filter:
            calculations = db_manager.get_calculations_by_weather(weather_filter)
        else:
            calculations = db_manager.get_all_calculations(limit)
        
        # Convert to dict format for JSON response
        calculations_data = calculations  # Already in dict format from database
        
        return jsonify({
            'success': True,
            'calculations': calculations_data,
            'total': len(calculations_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Gagal mengambil data perhitungan: {str(e)}'
        }), 500

@app.route('/api/calculations/recent')
def get_recent_calculations():
    """API endpoint untuk mendapatkan perhitungan terbaru"""
    try:
        days = request.args.get('days', 7, type=int)
        calculations = db_manager.get_recent_calculations(days)
        
        # Convert to dict format for JSON response
        calculations_data = [calc.to_dict() for calc in calculations]
        
        return jsonify({
            'success': True,
            'calculations': calculations_data,
            'total': len(calculations_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Gagal mengambil data perhitungan terbaru: {str(e)}'
        }), 500

@app.route('/api/statistics')
def get_statistics():
    """API endpoint untuk mendapatkan statistik perhitungan"""
    try:
        insights = db_manager.get_insights()
        
        # Extract key statistics
        stats = {
            'total_calculations': insights.get('total_calculations', 0),
            'weather_distribution': insights.get('weather_distribution', {}),
            'need_level_distribution': insights.get('need_level_distribution', {}),
            'average_duration_by_weather': insights.get('average_duration_by_weather', {}),
            'humidity_ranges': insights.get('humidity_ranges', {})
        }
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Gagal mengambil statistik: {str(e)}'
        }), 500

# Endpoint untuk reset data fuzzy (opsional)
@app.route('/api/reset-fuzzy', methods=['POST'])
def reset_fuzzy_data():
    """Reset data fuzzy untuk kembali ke mode dummy sensor"""
    global latest_fuzzy_result
    
    latest_fuzzy_result = {
        'timestamp': None,
        'kelembaban_input': None,
        'cuaca_input': None,
        'durasi_output': None,
        'tingkat_output': None,
        'is_active': False
    }
    
    return jsonify({
        'success': True,
        'message': 'Data fuzzy telah direset, monitoring kembali ke mode dummy'
    })

@app.route('/api/monitoring-history')
def get_monitoring_history():
    """API endpoint untuk mendapatkan data historis monitoring"""
    history_data = []
    current_time = datetime.datetime.now()
    
    # Generate 24 hours of dummy historical data (every hour)
    for i in range(24):
        timestamp = current_time - datetime.timedelta(hours=i)
        data_point = {
            'waktu': timestamp.strftime('%H:%M'),
            'kelembaban_tanah': round(random.uniform(20, 80), 1),
            'suhu': round(random.uniform(20, 35), 1),
            'udara': round(random.uniform(40, 90), 1),
            'hujan': round(random.uniform(0, 50), 1),
            'status_pompa': random.choice(['ON', 'OFF']),
            'durasi_penyiraman': round(random.uniform(0, 45), 1)
        }
        history_data.append(data_point)
    
    return jsonify(history_data[::-1])  # Reverse to show chronological order

if __name__ == '__main__':
    app.run(debug=True)