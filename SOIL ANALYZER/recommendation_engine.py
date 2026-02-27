"""
Crop Recommendation Engine - Enhanced Version
Analyzes soil parameters and provides comprehensive crop recommendations.
With detailed reporting and data-driven insights from data_core.json.
"""

import json
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime


class CropRecommendationEngine:
    def __init__(self, database_path: str = "crop_database.json", data_core_path: str = "data_core.json"):
        """Initialize the recommendation engine with crop database and data core."""
        self.crops = []
        self.data_core = []
        self.data_analysis = {}
        
        self.load_database(database_path)
        self.load_data_core(data_core_path)
        
        if self.data_core:
            self.analyze_data_core()
    
    def load_database(self, database_path: str):
        """Load crop data from JSON database."""
        try:
            with open(database_path, 'r') as f:
                data = json.load(f)
                self.crops = data['crops']
        except FileNotFoundError:
            print(f"Database not found: {database_path}")
            self.crops = []
        except json.JSONDecodeError:
            print(f"Invalid JSON in database: {database_path}")
            self.crops = []
    
    def load_data_core(self, data_core_path: str):
        """Load data_core.json containing historical soil/crop data."""
        try:
            with open(data_core_path, 'r') as f:
                self.data_core = json.load(f)
            print(f"Loaded {len(self.data_core)} records from data_core.json")
        except FileNotFoundError:
            print(f"Data core not found: {data_core_path}")
            self.data_core = []
        except json.JSONDecodeError:
            print(f"Invalid JSON in data core: {data_core_path}")
            self.data_core = []
    
    def analyze_data_core(self):
        """Analyze data_core.json to extract patterns and statistics."""
        if not self.data_core:
            return
        
        analysis = {
            'crop_stats': defaultdict(lambda: {
                'count': 0, 'temps': [], 'humidity': [], 'moisture': [],
                'nitrogen': [], 'phosphorous': [], 'potassium': [],
                'soil_types': defaultdict(int), 'fertilizers': defaultdict(int)
            }),
            'soil_type_stats': defaultdict(lambda: {'count': 0, 'crops': defaultdict(int)}),
            'fertilizer_stats': defaultdict(lambda: {'count': 0, 'crops': defaultdict(int)}),
            'temperature_range': {'min': float('inf'), 'max': float('-inf')},
            'humidity_range': {'min': float('inf'), 'max': float('-inf')},
            'moisture_range': {'min': float('inf'), 'max': float('-inf')}
        }
        
        for record in self.data_core:
            crop_type = record.get('Crop Type', 'Unknown')
            soil_type = record.get('Soil Type', 'Unknown')
            fertilizer = record.get('Fertilizer Name', 'Unknown')
            
            crop_stats = analysis['crop_stats'][crop_type]
            crop_stats['count'] += 1
            
            if 'Temparature' in record:
                temp = record['Temparature']
                crop_stats['temps'].append(temp)
                analysis['temperature_range']['min'] = min(analysis['temperature_range']['min'], temp)
                analysis['temperature_range']['max'] = max(analysis['temperature_range']['max'], temp)
            
            if 'Humidity' in record:
                hum = record['Humidity']
                crop_stats['humidity'].append(hum)
                analysis['humidity_range']['min'] = min(analysis['humidity_range']['min'], hum)
                analysis['humidity_range']['max'] = max(analysis['humidity_range']['max'], hum)
            
            if 'Moisture' in record:
                moist = record['Moisture']
                crop_stats['moisture'].append(moist)
                analysis['moisture_range']['min'] = min(analysis['moisture_range']['min'], moist)
                analysis['moisture_range']['max'] = max(analysis['moisture_range']['max'], moist)
            
            if 'Nitrogen' in record:
                crop_stats['nitrogen'].append(record['Nitrogen'])
            if 'Phosphorous' in record:
                crop_stats['phosphorous'].append(record['Phosphorous'])
            if 'Potassium' in record:
                crop_stats['potassium'].append(record['Potassium'])
            
            crop_stats['soil_types'][soil_type] += 1
            crop_stats['fertilizers'][fertilizer] += 1
            
            soil_stats = analysis['soil_type_stats'][soil_type]
            soil_stats['count'] += 1
            soil_stats['crops'][crop_type] += 1
            
            fert_stats = analysis['fertilizer_stats'][fertilizer]
            fert_stats['count'] += 1
            fert_stats['crops'][crop_type] += 1
        
        # Calculate averages and stats
        for crop_type, stats in analysis['crop_stats'].items():
            if stats['temps']:
                stats['avg_temp'] = sum(stats['temps']) / len(stats['temps'])
                stats['temp_std'] = self._calculate_std(stats['temps'])
            if stats['humidity']:
                stats['avg_humidity'] = sum(stats['humidity']) / len(stats['humidity'])
            if stats['moisture']:
                stats['avg_moisture'] = sum(stats['moisture']) / len(stats['moisture'])
            if stats['nitrogen']:
                stats['avg_nitrogen'] = sum(stats['nitrogen']) / len(stats['nitrogen'])
            if stats['phosphorous']:
                stats['avg_phosphorous'] = sum(stats['phosphorous']) / len(stats['phosphorous'])
            if stats['potassium']:
                stats['avg_potassium'] = sum(stats['potassium']) / len(stats['potassium'])
            
            if stats['soil_types']:
                sorted_soils = sorted(stats['soil_types'].items(), key=lambda x: x[1], reverse=True)
                stats['most_common_soil'] = sorted_soils[0][0]
                stats['soil_distribution'] = {k: round(v/stats['count']*100, 1) for k, v in sorted_soils[:3]}
            
            if stats['fertilizers']:
                sorted_ferts = sorted(stats['fertilizers'].items(), key=lambda x: x[1], reverse=True)
                stats['most_common_fertilizer'] = sorted_ferts[0][0]
                stats['fertilizer_distribution'] = {k: round(v/stats['count']*100, 1) for k, v in sorted_ferts[:5]}
        
        self.data_analysis = analysis
        print("Data core analysis complete!")
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def calculate_suitability(self, crop: Dict, soil_data: Dict) -> Tuple[float, Dict]:
        """Calculate suitability score with detailed breakdown."""
        scores = {}
        weights = {
            'ph': 15, 'nitrogen': 20, 'phosphorus': 15,
            'potassium': 15, 'moisture': 15, 'temperature': 12, 'rainfall': 8
        }
        
        ph = soil_data.get('ph', 7.0)
        ph_min, ph_max = crop.get('ph_min', 5.0), crop.get('ph_max', 8.0)
        
        if ph_min <= ph <= ph_max:
            ph_score = 100
        elif ph < ph_min:
            ph_score = max(0, 100 - (ph_min - ph) * 25)
        else:
            ph_score = max(0, 100 - (ph - ph_max) * 25)
        scores['ph'] = ph_score
        
        for nutrient in ['nitrogen', 'phosphorus', 'potassium']:
            required = crop.get(f'{nutrient}_requirement', 'medium')
            provided = soil_data.get(nutrient, 'medium')
            scores[nutrient] = self._nutrient_score(required, provided)
        
        moisture_req = crop.get('moisture_requirement', 'moderate')
        moisture_prov = soil_data.get('moisture', 'moderate')
        scores['moisture'] = self._moisture_score(moisture_req, moisture_prov)
        
        temp = soil_data.get('temperature', 20)
        temp_min, temp_max = crop.get('temperature_min', 10), crop.get('temperature_max', 35)
        
        if temp_min <= temp <= temp_max:
            temp_score = 100
        elif temp < temp_min:
            temp_score = max(0, 100 - (temp_min - temp) * 8)
        else:
            temp_score = max(0, 100 - (temp - temp_max) * 8)
        scores['temperature'] = temp_score
        
        rainfall = soil_data.get('rainfall', 500)
        rain_min, rain_max = crop.get('rainfall_min', 300), crop.get('rainfall_max', 1500)
        
        if rain_min <= rainfall <= rain_max:
            rain_score = 100
        elif rainfall < rain_min:
            rain_score = max(0, 100 - (rain_min - rainfall) / 15)
        else:
            rain_score = max(0, 100 - (rainfall - rain_max) / 25)
        scores['rainfall'] = rain_score
        
        total_score = sum(scores[key] * weights[key] / 100 for key in weights)
        
        return total_score, scores
    
    def _nutrient_score(self, required: str, provided: str) -> float:
        """Calculate nutrient match score."""
        levels = {'very_low': 1, 'low': 2, 'medium': 3, 'high': 4, 'very_high': 5}
        
        req_level = levels.get(required.lower(), 3)
        prov_level = levels.get(provided.lower(), 3)
        
        difference = abs(req_level - prov_level)
        
        if difference == 0:
            return 100
        elif difference == 1:
            return 75
        elif difference == 2:
            return 50
        else:
            return 25
    
    def _moisture_score(self, required: str, provided: str) -> float:
        """Calculate moisture match score."""
        levels = {'very_low': 1, 'low': 2, 'moderate': 3, 'high': 4, 'very_high': 5}
        
        req_level = levels.get(required.lower(), 3)
        prov_level = levels.get(provided.lower(), 3)
        
        difference = abs(req_level - prov_level)
        
        if difference == 0:
            return 100
        elif difference == 1:
            return 70
        elif difference == 2:
            return 40
        else:
            return 20
    
    def find_similar_records(self, soil_data: Dict, top_n: int = 10) -> List[Dict]:
        """Find similar records from data_core."""
        if not self.data_core:
            return []
        
        nitrogen_map = {'very_low': 5, 'low': 15, 'medium': 30, 'high': 45, 'very_high': 60}
        nitrogen_val = nitrogen_map.get(soil_data.get('nitrogen', 'medium').lower(), 30)
        
        moisture_map = {'very_low': 15, 'low': 30, 'moderate': 50, 'high': 70, 'very_high': 85}
        moisture_num = moisture_map.get(soil_data.get('moisture', 'moderate').lower(), 50)
        
        similarities = []
        
        for record in self.data_core:
            score = 0
            
            temp_diff = abs(record.get('Temparature', 25) - soil_data.get('temperature', 25))
            temp_score = max(0, 30 - temp_diff * 2)
            
            moist_diff = abs(record.get('Moisture', 50) - moisture_num)
            moist_score = max(0, 20 - moist_diff * 0.5)
            
            n_diff = abs(record.get('Nitrogen', 25) - nitrogen_val)
            npk_score = max(0, 30 - n_diff * 0.5)
            
            total_score = temp_score + moist_score + npk_score
            
            similarities.append({
                'record': record,
                'score': total_score,
                'crop': record.get('Crop Type'),
                'soil_type': record.get('Soil Type'),
                'fertilizer': record.get('Fertilizer Name'),
                'temperature': record.get('Temparature'),
                'humidity': record.get('Humidity'),
                'moisture': record.get('Moisture'),
                'nitrogen': record.get('Nitrogen'),
                'phosphorous': record.get('Phosphorous'),
                'potassium': record.get('Potassium')
            })
        
        similarities.sort(key=lambda x: x['score'], reverse=True)
        return similarities[:top_n]
    
    def get_recommendations(self, soil_data: Dict, top_n: int = 10) -> Dict:
        """Get comprehensive recommendations."""
        if not self.crops:
            return {"error": "No crops in database"}
        
        crop_scores = []
        for crop in self.crops:
            score, breakdown = self.calculate_suitability(crop, soil_data)
            crop_scores.append({'crop': crop, 'score': score, 'breakdown': breakdown})
        
        crop_scores.sort(key=lambda x: x['score'], reverse=True)
        
        primary = [c for c in crop_scores if c['score'] >= 60]
        secondary = [c for c in crop_scores if 40 <= c['score'] < 60]
        poor = [c for c in crop_scores if c['score'] < 40]
        
        similar_records = self.find_similar_records(soil_data, top_n=10)
        
        soil_analysis = self._comprehensive_soil_analysis(soil_data)
        fertilizer_recs = self._detailed_fertilizer_recommendations(soil_data)
        irrigation_recs = self._detailed_irrigation_recommendations(soil_data)
        data_insights = self._generate_comprehensive_insights(soil_data, primary)
        risk_analysis = self._analyze_risks(soil_data, primary)
        crop_rotation = self._generate_crop_rotation_plan(primary, secondary)
        seasonal_recs = self._get_seasonal_recommendations(primary)
        
        return {
            'soil_data': soil_data,
            'timestamp': datetime.now().isoformat(),
            'analysis': soil_analysis,
            'primary_crops': primary[:top_n],
            'secondary_crops': secondary[:5],
            'poor_crops': poor[:3],
            'similar_records': similar_records,
            'fertilizer_recommendations': fertilizer_recs,
            'irrigation_recommendations': irrigation_recs,
            'data_insights': data_insights,
            'risk_analysis': risk_analysis,
            'crop_rotation_plan': crop_rotation,
            'seasonal_recommendations': seasonal_recs,
            'yield_estimates': self._estimate_yields(primary, soil_data)
        }
    
    def _comprehensive_soil_analysis(self, soil_data: Dict) -> Dict:
        """Generate comprehensive soil analysis."""
        analysis = {}
        
        ph = soil_data.get('ph', 7.0)
        if ph < 4.5:
            ph_status = "Cok Asidik"
            ph_advice = "Kirec uygulamasi siddetle onerir"
            suitable_crops = ["Cay", "Kahve", "Yaban Mersini"]
        elif ph < 5.5:
            ph_status = "Asidik"
            ph_advice = "Kirec veya dolomit uygulanmali"
            suitable_crops = ["Patates", "Nohut", "Mercimek", "Sebzeler"]
        elif ph < 6.5:
            ph_status = "Hafif Asidik"
            ph_advice = "Hafif kirecleme faydali olabilir"
            suitable_crops = ["Bugday", "Misir", "Aycicegi"]
        elif ph < 7.5:
            ph_status = "Notr"
            ph_advice = "Ideal aralik, mevcut durumu koruyun"
            suitable_crops = ["Cogu bitki için ideal"]
        elif ph < 8.5:
            ph_status = "Alkalik"
            ph_advice = "Kukurt veya asitli gubreler kullanin"
            suitable_crops = ["Arpa", "Pamuk", "Kuskonmaz"]
        else:
            ph_status = "Cok Alkalik"
            ph_advice = "Toprak islahi gerekli"
            suitable_crops = ["Dayanikli bitkiler"]
        
        analysis['ph'] = {'value': ph, 'status': ph_status, 'advice': ph_advice, 'suitable_crops': suitable_crops}
        
        nutrients = {}
        for nutrient in ['nitrogen', 'phosphorus', 'potassium']:
            level = soil_data.get(nutrient, 'medium')
            
            if level == 'very_low':
                status = "Cok Dusuk"
                color = "danger"
                action = f"{nutrient.capitalize()} gubresi hemen uygulanmali"
            elif level == 'low':
                status = "Dusuk"
                color = "warning"
                action = f"{nutrient.capitalize()} tavsiyesi onerir"
            elif level == 'medium':
                status = "Orta"
                color = "success"
                action = "Mevcut seviye yeterli, izlemeye devam edin"
            elif level == 'high':
                status = "Yuksek"
                color = "info"
                action = "Dikkatli gubreleme yapin"
            else:
                status = "Cok Yuksek"
                color = "danger"
                action = "Gubrelemeyi durdurun, toprak testi yapin"
            
            nutrients[nutrient] = {'level': level, 'status': status, 'color': color, 'action': action}
        
        analysis['nutrients'] = nutrients
        
        moisture = soil_data.get('moisture', 'moderate')
        if moisture in ['very_low', 'low']:
            moisture_status = "Kuru"
            action = "Damla sulama ve malclama siddetle onerir"
        elif moisture == 'moderate':
            moisture_status = "Orta"
            action = "Standart sulama programi yeterli"
        else:
            moisture_status = "Nemli"
            action = "Drenaj sistemi kontrol edin"
        
        analysis['moisture'] = {'status': moisture_status, 'action': action}
        
        n, p, k = soil_data.get('nitrogen', 'medium'), soil_data.get('phosphorus', 'medium'), soil_data.get('potassium', 'medium')
        
        if all(x in ['medium', 'high'] for x in [n, p, k]):
            overall = "Mukemmel - Cogu bitki için ideal kosullar"
            score = 90
        elif any(x in ['very_low', 'low'] for x in [n, p, k]):
            overall = "Gelisme Gerekli - Besin tavsiyesi onerir"
            score = 50
        else:
            overall = "Orta - Bazi iyilestirmeler faydali olabilir"
            score = 70
        
        analysis['overall'] = {'status': overall, 'score': score}
        analysis['climate'] = {'temperature': soil_data.get('temperature', 20), 'rainfall': soil_data.get('rainfall', 500), 'region': soil_data.get('region', 'any')}
        
        return analysis
    
    def _detailed_fertilizer_recommendations(self, soil_data: Dict) -> Dict:
        """Generate detailed fertilizer recommendations."""
        recommendations = {'immediate': [], 'long_term': [], 'organic': [], 'mineral': []}
        
        nitrogen = soil_data.get('nitrogen', 'medium')
        phosphorus = soil_data.get('phosphorus', 'medium')
        potassium = soil_data.get('potassium', 'medium')
        
        if nitrogen in ['very_low', 'low']:
            recommendations['immediate'].append({'type': 'Azot', 'product': 'Ure (46-0-0)', 'dose': '40-60 kg/da', 'timing': 'Ekimden 2-3 hafta sonra', 'method': 'Yapraktan veya topraha serpme'})
            recommendations['mineral'].append("CAN (Kalsiyum Amonyum Nitrat) - 25-30 kg/da")
            recommendations['organic'].append("Hayvan gubresi - 2-3 ton/da (kompostlanmis)")
            recommendations['organic'].append("Yesil gubreleme (baklagiller)")
        
        if phosphorus in ['very_low', 'low']:
            recommendations['immediate'].append({'type': 'Fosfor', 'product': 'DAP (Di-Amonyum Fosfat)', 'dose': '30-40 kg/da', 'timing': 'Ekim ekimle birlikte', 'method': 'Tohumla birlikte veya sira uzeri'})
            recommendations['mineral'].append("TSP (Triple Super Fosfat) - 25-35 kg/da")
            recommendations['organic'].append("Kemik unu - 100-150 kg/da")
        
        if potassium in ['very_low', 'low']:
            recommendations['immediate'].append({'type': 'Potasyum', 'product': 'MOP (Muriyat Potas)', 'dose': '25-30 kg/da', 'timing': 'Ekimden once veya sonraki donemlerde', 'method': 'Topraha serpme veya damla sulama ile'})
            recommendations['mineral'].append("SOP (Sulfat Potas) - 20-25 kg/da")
            recommendations['organic'].append("Odun kulü - 100-150 kg/da")
        
        if nitrogen == 'medium' and phosphorus == 'medium' and potassium == 'medium':
            recommendations['immediate'].append({'type': 'Dengeli Beslenme', 'product': 'NPK 15-15-15', 'dose': '40-50 kg/da', 'timing': 'Ekimden 3-4 hafta sonra', 'method': 'Topraha serpme'})
        
        recommendations['micronutrients'] = [
            {'element': 'Demir (Fe)', 'deficiency': 'Sararma', 'product': 'Demir selat', 'dose': '50-100 g/da'},
            {'element': 'Cinko (Zn)', 'deficiency': 'Kucuk yapraklar', 'product': 'Cinko selat', 'dose': '30-50 g/da'},
            {'element': 'Mangan (Mn)', 'deficiency': 'Damarlar arasi kloroz', 'product': 'Mangan selat', 'dose': '40-60 g/da'},
            {'element': 'Bor (B)', 'deficiency': 'Cicek dokumu', 'product': 'Bor asidi', 'dose': '20-30 g/da'}
        ]
        
        return recommendations
    
    def _detailed_irrigation_recommendations(self, soil_data: Dict) -> Dict:
        """Generate detailed irrigation recommendations."""
        recommendations = {}
        
        moisture = soil_data.get('moisture', 'moderate')
        rainfall = soil_data.get('rainfall', 500)
        temp = soil_data.get('temperature', 20)
        
        if moisture in ['very_low', 'low']:
            recommendations['method'] = "Damla Sulama + Malclama"
            recommendations['priority'] = "COK YUKSEK"
            recommendations['frequency'] = "Gunde 1-2 kez, kisa sureli"
            recommendations['water_saving'] = "Damla ile %40-60 su tasarrufu saglanir"
        elif moisture == 'moderate':
            recommendations['method'] = "Klasik Sulama veya Damla"
            recommendations['priority'] = "ORTA"
            recommendations['frequency'] = "Haftada 2-3 kez"
        else:
            recommendations['method'] = "Drenaj Odakli"
            recommendations['priority'] = "DRENAJ ONCELIKLI"
            recommendations['frequency'] = "Sulama minimum, yagis takibi"
        
        if rainfall < 300:
            recommendations['supplement'] = "Ek sulama sistemi siddetle onerir"
            recommendations['harvesting'] = "Yagmur suyu hasadi sistemi kurulmali"
        elif rainfall < 500:
            recommendations['supplement'] = "Destekleyici sulama gerekebilir"
        
        if temp > 30:
            recommendations['heat_management'] = "Sik sulama + golgeleme onerir"
            recommendations['evaporation_risk'] = "Yuksek buharlasma - sabah erken sulayin"
        elif temp < 15:
            recommendations['heat_management'] = "Az sulama - asiri nem mantar riski"
        
        recommendations['critical_stages'] = [
            "Cimlenme/Cikis: Yuksek nem gerekli",
            "Vegetatif Buyume: Duzenli sulama",
            "Ciceklenme: Kritik donem - stres yok",
            "Meyve/Dane Dolumu: Yuksek su ihtiyaci"
        ]
        
        return recommendations
    
    def _generate_comprehensive_insights(self, soil_data: Dict, primary_crops: List[Dict]) -> Dict:
        """Generate comprehensive data-driven insights."""
        insights = {'crop_specific': [], 'soil_improvement': [], 'historical': []}
        
        if not primary_crops:
            return insights
        
        for crop_rec in primary_crops[:3]:
            crop = crop_rec['crop']
            crop_name = crop.get('name', '')
            
            crop_name_map = {
                'Wheat': 'Wheat', 'Rice': 'Paddy', 'Paddy': 'Paddy',
                'Maize': 'Maize', 'Barley': 'Barley', 'Cotton': 'Cotton',
                'Sugarcane': 'Sugarcane', 'Millet': 'Millets', 'Millets': 'Millets',
                'Pulses': 'Pulses', 'Ground Nuts': 'Ground Nuts', 'Oil Seeds': 'Oil Seeds',
                'Tobacco': 'Tobacco', 'Lentils': 'Pulses', 'Chickpeas': 'Pulses'
            }
            
            data_core_crop = crop_name_map.get(crop_name, crop_name)
            
            if self.data_analysis and data_core_crop in self.data_analysis['crop_stats']:
                stats = self.data_analysis['crop_stats'][data_core_crop]
                
                insight = {'crop': crop_name, 'score': crop_rec['score'], 'optimal_conditions': {}}
                
                if 'avg_temp' in stats:
                    insight['optimal_conditions']['temperature'] = {
                        'ideal': f"{stats['avg_temp']:.1f}C",
                        'range': f"{min(stats['temps']):.0f}-{max(stats['temps']):.0f}C",
                        'data_points': len(stats['temps'])
                    }
                
                if 'avg_humidity' in stats:
                    insight['optimal_conditions']['humidity'] = {
                        'ideal': f"{stats['avg_humidity']:.1f}%",
                        'data_points': len(stats['humidity'])
                    }
                
                if 'most_common_soil' in stats:
                    insight['optimal_conditions']['soil'] = stats['most_common_soil']
                
                if 'soil_distribution' in stats:
                    insight['optimal_conditions']['soil_preferences'] = stats['soil_distribution']
                
                if 'most_common_fertilizer' in stats:
                    insight['optimal_conditions']['fertilizer'] = stats['most_common_fertilizer']
                
                if 'fertilizer_distribution' in stats:
                    insight['optimal_conditions']['fertilizer_options'] = stats['fertilizer_distribution']
                
                insights['crop_specific'].append(insight)
        
        nitrogen = soil_data.get('nitrogen', 'medium')
        if nitrogen in ['low', 'very_low']:
            insights['soil_improvement'].append({
                'issue': 'Dusuk Azot', 'solution': 'Baklagil ekim rotasyonu', 'timeline': '1-2 sezon', 'crops': ['Nohut', 'Mercimek', 'Yonca', 'Ucgul']
            })
        
        phosphorus = soil_data.get('phosphorus', 'medium')
        if phosphorus in ['low', 'very_low']:
            insights['soil_improvement'].append({
                'issue': 'Dusuk Fosfor', 'solution': 'Organik madde ilavesi + fosfat kayasi', 'timeline': '2-3 sezon', 'crops': ['Fig', 'Yonca']
            })
        
        if self.data_core:
            total_records = len(self.data_core)
            insights['historical'] = {'database_size': f"{total_records:,} kayit", 'reliability': 'YUKSEK' if total_records > 5000 else 'ORTA', 'coverage': 'Kapsamli veri seti kullanildi'}
        
        return insights
    
    def _analyze_risks(self, soil_data: Dict, primary_crops: List[Dict]) -> Dict:
        """Analyze potential risks."""
        risks = {'environmental': [], 'agronomic': [], 'market': []}
        
        if soil_data.get('rainfall', 500) < 300:
            risks['environmental'].append({'type': 'Kuraklik Riski', 'severity': 'YUKSEK', 'mitigation': 'Damla sulama ve yagmur suyu hasadi sistemi kurulmali'})
        
        if soil_data.get('moisture', 'moderate') == 'high':
            risks['environmental'].append({'type': 'Fungal Hastalik Riski', 'severity': 'ORTA-YUKSEK', 'mitigation': 'Fungisit uygulamasi ve iyi havalandirma'})
        
        ph = soil_data.get('ph', 7.0)
        if ph < 5.5 or ph > 8.0:
            risks['agronomic'].append({'type': 'Besin Emilimi Sorunu', 'severity': 'YUKSEK', 'mitigation': 'Toprak pH\'sini duzeltmek için kirec/kukurt uygulayin'})
        
        if primary_crops:
            top_crop = primary_crops[0]['crop']
            temp = soil_data.get('temperature', 20)
            
            if temp > top_crop.get('temperature_max', 35) - 5:
                risks['agronomic'].append({'type': 'Sicaklik Stresi', 'severity': 'ORTA', 'mitigation': 'Golgeleme ve sik sulama'})
        
        if primary_crops:
            for crop in primary_crops[:2]:
                category = crop['crop'].get('category', '')
                if category in ['Commercial', 'Fiber']:
                    risks['market'].append({'type': 'Fiyat Dalgalanmasi', 'severity': 'ORTA', 'mitigation': 'Cesitlendirme onerir'})
        
        return risks
    
    def _generate_crop_rotation_plan(self, primary: List[Dict], secondary: List[Dict]) -> Dict:
        """Generate crop rotation plan."""
        if not primary:
            return {'message': 'Oncelikli urun bulunamadi'}
        
        plan = {'current_season': primary[0]['crop'].get('name', 'Bilinmiyor'), 'next_season_crops': [], 'rotation_principles': [], 'benefits': []}
        
        current_category = primary[0]['crop'].get('category', '')
        
        if current_category == 'Cereal':
            plan['next_season_crops'] = [{'crop': 'Pulses (Baklagiller)', 'reason': 'Azot fiksasyonu saglar'}, {'crop': 'Oil Seeds (Yagli Tohumlar)', 'reason': 'Toprak yapisini iyilestirir'}]
            plan['rotation_principles'] = ['Tahil -> Baklagil -> Yagli tohum rotasyonu uygulayin', 'Her 3-4 yilda bir baklagil ekin', 'Nobetleme suresi en az 2 yil olmali']
            plan['benefits'] = ['Toprak azotunu dogal olarak artirir', 'Hastalik ve zararli dongusunu kirar', 'Organik madde icerigini yukseltir']
        
        elif current_category == 'Vegetable':
            plan['next_season_crops'] = [{'crop': 'Leafy Vegetables', 'reason': 'Farkli besin profili'}, {'crop': 'Root Vegetables', 'reason': 'Farkli kok derinligi'}]
            plan['rotation_principles'] = ['Sebzeleri familyalarina gore dondurun', 'Kok sebzeler -> Yaprak sebzeleri -> Meyveli sebzeler', 'Ayni familyadan bitkileri ardisik ekmeyin']
        
        elif current_category == 'Legume':
            plan['next_season_crops'] = [{'crop': 'Cereals (Tahillar)', 'reason': 'Azot kullanir'}, {'crop': 'Vegetables (Sebzeler)', 'reason': 'Besin acigini kapatir'}]
            plan['rotation_principles'] = ['Baklagilleri her yil ayni parsellerde ekin', 'Azot fiksasyonunu maksimize etmek için karisik ekim yapin', 'Baklagil hasadindan sonra anizi topraha karistirin']
        
        return plan
    
    def _get_seasonal_recommendations(self, primary: List[Dict]) -> Dict:
        """Get seasonal recommendations."""
        recommendations = {'spring': [], 'summer': [], 'fall': [], 'winter': []}
        
        if not primary:
            return recommendations
        
        for crop in primary[:3]:
            crop_name = crop['crop'].get('name', '')
            seasons = crop['crop'].get('seasons', [])
            
            for season in seasons:
                if season in recommendations:
                    recommendations[season].append(crop_name)
        
        recommendations['spring'] = recommendations.get('spring', []) or ['Bugday', 'Arpa', 'Nohut']
        recommendations['summer'] = recommendations.get('summer', []) or ['Misir', 'Pamuk', 'Aycicegi']
        recommendations['fall'] = recommendations.get('fall', []) or ['Mercimek', 'Sarmisak', 'Sogan']
        recommendations['winter'] = recommendations.get('winter', []) or ['Bugday', 'Arpa', 'Kolza']
        
        return recommendations
    
    def _estimate_yields(self, primary: List[Dict], soil_data: Dict) -> Dict:
        """Estimate potential yields."""
        estimates = {}
        
        if not primary:
            return estimates
        
        for crop_rec in primary[:5]:
            crop = crop_rec['crop']
            crop_name = crop.get('name', '')
            suitability = crop_rec['score']
            
            category_yields = {
                'Cereal': {'low': 300, 'medium': 500, 'high': 800},
                'Vegetable': {'low': 1000, 'medium': 2000, 'high': 3500},
                'Fruit': {'low': 500, 'medium': 1000, 'high': 2000},
                'Legume': {'low': 150, 'medium': 250, 'high': 400},
                'Oilseed': {'low': 100, 'medium': 200, 'high': 350},
                'Commercial': {'low': 800, 'medium': 1500, 'high': 2500}
            }
            
            category = crop.get('category', 'Cereal')
            base_yields = category_yields.get(category, {'low': 200, 'medium': 400, 'high': 600})
            
            if suitability >= 80:
                yield_estimate = base_yields['high']
            elif suitability >= 60:
                yield_estimate = base_yields['medium']
            else:
                yield_estimate = base_yields['low']
            
            yield_estimate = yield_estimate * (suitability / 100)
            
            estimates[crop_name] = {'estimated_yield': f"{yield_estimate:.0f} kg/da", 'suitability_score': f"{suitability:.1f}%", 'confidence': 'YUKSEK' if suitability >= 70 else 'ORTA'}
        
        return estimates


def get_quick_recommendation(soil_data: Dict) -> Dict:
    """Quick function to get recommendations."""
    engine = CropRecommendationEngine()
    return engine.get_recommendations(soil_data)


if __name__ == "__main__":
    test_soil = {'ph': 6.8, 'nitrogen': 'medium', 'phosphorus': 'low', 'potassium': 'high', 'moisture': 'moderate', 'temperature': 22, 'rainfall': 800, 'region': 'any'}
    
    engine = CropRecommendationEngine()
    results = engine.get_recommendations(test_soil)
    
    print("=" * 60)
    print("DETAYLI TOPRAK ANALIZI VE URUN ONERILERI")
    print("=" * 60)
    
    print("\n📊 TOPRAK ANALIZI:")
    print(f"  pH Degeri: {results['analysis']['ph']['value']}")
    print(f"  pH Durumu: {results['analysis']['ph']['status']}")
    print(f"  Oneri: {results['analysis']['ph']['advice']}")
    
    print("\n🥦 ONCELIKLI URUNLER:")
    for i, crop in enumerate(results['primary_crops'][:5], 1):
        print(f"  {i}. {crop['crop']['name']} - Uygunluk: %{crop['score']:.1f}")
    
    print("\n💧 SULAMA ONERILERI:")
    irr = results['irrigation_recommendations']
    print(f"  Yontem: {irr.get('method', 'N/A')}")
    print(f"  Oncelik: {irr.get('priority', 'N/A')}")
    print(f"  Siklik: {irr.get('frequency', 'N/A')}")
    
    print("\n💊 GUBRELEME ONERILERI:")
    for rec in results['fertilizer_recommendations'].get('immediate', [])[:3]:
        print(f"  - {rec.get('type')}: {rec.get('product')} ({rec.get('dose')})")

