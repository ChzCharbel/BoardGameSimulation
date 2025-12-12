// Funciones para la página principal
document.addEventListener("DOMContentLoaded", function () {
  const createSimulationBtn = document.getElementById("create-simulation");

  if (createSimulationBtn) {
    createSimulationBtn.addEventListener("click", createNewSimulation);
  }
});

async function createNewSimulation() {
  try {
    const response = await fetch("/api/create_simulation", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.simulation_id) {
      // Redirigir a la página de simulación con el ID
      window.location.href = `/simulation?id=${data.simulation_id}`;
    } else {
      alert("Error al crear la simulación");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Error al crear la simulación");
  }
}
