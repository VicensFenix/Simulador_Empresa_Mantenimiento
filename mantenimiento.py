import simpy
import random
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# --- Configuración interactiva ---
print("🖥️ SIMULADOR DE MANTENIMIENTO DE HARDWARE 🖥️")

# 1. Datos de técnicos (configuración uniforme)
def ingresar_empleados():
    print("\n👨‍💼 CONFIGURACIÓN DE TÉCNICOS")
    num_tecnicos = int(input("👉 Cantidad de técnicos: "))
    horas_semana = float(input("⏰ Horas base por semana (ej: 40): "))
    salario_hora = float(input("💰 Salario por hora normal (ej: 15): $"))
    salario_extra = float(input("💸 Salario por hora extra (ej: 22): $"))
    
    return [{
        "horas_normales": horas_semana,
        "costo_hora": salario_hora,
        "costo_extra": salario_extra 
    } for _ in range(num_tecnicos)]

# 2. Herramientas para hardware
def ingresar_herramientas():
    herramientas = []
    print("\n🧰 REGISTRO DE HERRAMIENTAS")
    while True:
        nombre = input("\n🔧 Nombre (ej: 'Multímetro'): ")
        if not nombre:
            if herramientas:
                break
            print("¡Debes registrar al menos 1 herramienta!")
            continue
        
        precio = float(input("💵 Precio: $"))
        vida_util = int(input("🔄 Vida útil (en reparaciones): "))
        
        herramientas.append({
            "nombre": nombre,
            "precio": precio,
            "vida_util": vida_util,
            "usos": 0
        })
    return herramientas

# 3. Servicios de hardware
def ingresar_servicios():
    servicios = {}
    print("\n🔩 SERVICIOS DISPONIBLES")
    while True:
        nombre = input("\n🖥️ Nombre del servicio (ej: 'Limpieza interna'): ")
        if not nombre:
            break
        
        costo = float(input("💲 Costo del servicio: $"))
        servicios[nombre] = costo
    
    return servicios

# --- Simulación Principal ---
def ejecutar_simulacion(tecnicos, herramientas, servicios, dias):
    env = simpy.Environment()
    stats = {
        "costos": [],
        "servicios": defaultdict(int),
        "herramientas": defaultdict(int)
    }

    def realizar_reparacion(env, tecnico):
        # Selección de servicio
        if servicios:
            servicio, costo = random.choice(list(servicios.items()))
        else:
            servicio, costo = "Reparación genérica", random.uniform(50, 200)
        
        stats["servicios"][servicio] += 1
        
        # Tiempo de reparación (0.5 a 3 horas)
        tiempo = random.uniform(0.5, 3)
        yield env.timeout(tiempo)
        
        # Costos
        hora_actual = env.now % 24
        dia_actual = int(env.now // 24)
        
        if hora_actual < 8 or hora_actual > 18:  # Horario nocturno
            costo_mano_obra = tiempo * tecnico["costo_extra"]
        else:
            costo_mano_obra = tiempo * tecnico["costo_hora"]
        
        # Desgaste de herramientas
        herramienta = random.choice(herramientas)
        stats["herramientas"][herramienta["nombre"]] += 1
        herramienta["usos"] += 1
        costo_herramienta = 0
        if herramienta["usos"] >= herramienta["vida_util"]:
            costo_herramienta = herramienta["precio"]
            herramienta["usos"] = 0
        
        # Registrar costos
        if not stats["costos"] or stats["costos"][-1]["dia"] != dia_actual:
            stats["costos"].append({
                "dia": dia_actual,
                "servicios": 0,
                "mano_obra": 0,
                "herramientas": 0
            })
        
        stats["costos"][-1]["servicios"] += costo
        stats["costos"][-1]["mano_obra"] += costo_mano_obra
        stats["costos"][-1]["herramientas"] += costo_herramienta

        # Mostrar progreso
        print(f"\n🔧 Día {dia_actual+1} - {hora_actual:02.0f}:00")
        print(f"• Servicio: {servicio} (${costo:.2f})")
        print(f"• Técnico: {tiempo:.1f} horas trabajadas")
        print(f"• Herramienta usada: {herramienta['nombre']}")

    def generar_trabajos(env):
        while True:
            yield env.timeout(random.expovariate(1/2))  # 1 trabajo cada 2 horas en promedio
            env.process(realizar_reparacion(env, random.choice(tecnicos)))

    print("\n⚙️ INICIANDO SIMULACIÓN...")
    env.process(generar_trabajos(env))
    env.run(until=dias*24)
    
    return stats

# --- Visualización de Resultados ---
def mostrar_resultados(stats, dias):
    # Procesar datos
    dias_sim = [d["dia"]+1 for d in stats["costos"]]
    acum_servicios = np.cumsum([d["servicios"] for d in stats["costos"]])
    acum_mano_obra = np.cumsum([d["mano_obra"] for d in stats["costos"]])
    acum_herramientas = np.cumsum([d["herramientas"] for d in stats["costos"]])
    total = acum_servicios + acum_mano_obra + acum_herramientas
    
    # Gráfico 1: Evolución de costos
    plt.figure(figsize=(12, 6))
    plt.plot(dias_sim, acum_servicios, label="Servicios", marker='o')
    plt.plot(dias_sim, acum_mano_obra, label="Mano de obra", marker='s')
    plt.plot(dias_sim, acum_herramientas, label="Herramientas", marker='^')
    plt.plot(dias_sim, total, label="TOTAL", linestyle='--', linewidth=2, color='red')
    
    plt.title(f"📈 COSTOS ACUMULADOS ({dias} DÍAS)", pad=20)
    plt.xlabel("Día de operación")
    plt.ylabel("Costos ($)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Gráfico 2: Frecuencia de servicios
    plt.figure(figsize=(12, 4))
    servicios = list(stats["servicios"].keys())
    frecuencias = list(stats["servicios"].values())
    plt.bar(servicios, frecuencias, color='skyblue')
    plt.title("📊 FRECUENCIA DE SERVICIOS")
    plt.xticks(rotation=45)
    plt.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.show()

    # Reporte final
    print("\n" + "="*50)
    print(f"📑 INFORME FINAL - {dias} DÍAS".center(50))
    print("="*50)
    print(f"\n🔧 Servicios realizados: {sum(stats['servicios'].values())}")
    print(f"💰 Costo total: ${total[-1]:,.2f}")
    print("\n🛠️ Herramientas más usadas:")
    for herramienta, usos in stats["herramientas"].items():
        print(f"• {herramienta}: {usos} usos")

# --- Ejecución Principal ---
if __name__ == "__main__":
    # Configuración
    tecnicos = ingresar_empleados()
    herramientas = ingresar_herramientas()
    servicios = ingresar_servicios()
    dias = int(input("\n📆 Días a simular: "))
    
    # Simulación
    estadisticas = ejecutar_simulacion(tecnicos, herramientas, servicios, dias)
    
    # Resultados
    mostrar_resultados(estadisticas, dias)
    input("\nPresione Enter para salir...")