import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-nuevo-credito',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './nuevo-credito.html'
})
export class NuevoCredito {
  
  private apiCrear = 'http://localhost:8000/api/creditos/crear/';
  private apiBuscar = 'http://localhost:8000/api/clientes/buscar/';

  // Esta variable controlará si las casillas de texto están bloqueadas o no en la pantalla
  clienteExiste: boolean = false;

  credito = {
    nombre_completo: '',
    cedula: '',
    telefono: '',
    direccion_residencia: '',
    capital_prestado: null,
    porcentaje_interes: 20,
    meses_duracion: 1,
    frecuencia_pago: 'diario'
  };

  constructor(private http: HttpClient) {}

  // 🧠 FUNCIÓN INTELIGENTE: Se dispara cada vez que el cobrador termina de escribir la cédula
  verificarCedula() {
    if (!this.credito.cedula) return;

    // Viajamos a Django a consultar la cédula en tiempo real
    this.http.get(`${this.apiBuscar}${this.credito.cedula}/`).subscribe({
      next: (res: any) => {
        if (res.existe) {
          // CASO A: El cliente ya existe. Auto-rellenamos los campos y los bloqueamos
          this.credito.nombre_completo = res.nombre_completo;
          this.credito.telefono = res.telefono;
          this.credito.direccion_residencia = res.direccion_residencia;
          this.clienteExiste = true; // Activa el candado visual
        } else {
          // CASO B: Es un cliente completamente nuevo. Limpiamos y desbloqueamos todo
          this.clienteExiste = false; // Abre el candado visual
          this.credito.nombre_completo = '';
          this.credito.telefono = '';
          this.credito.direccion_residencia = '';
        }
      },
      error: (err) => console.error('Error al consultar cédula:', err)
    });
  }

  guardarCredito() {
    // Disparamos la petición POST al backend
    this.http.post(this.apiCrear, this.credito).subscribe({
      next: (respuesta: any) => {
        alert('🎉 ¡Éxito! Crédito procesado y asignado correctamente.');
        this.limpiarFormulario();
      },
      error: (error) => {
        console.error('Error al conectar con Django:', error);
        alert('❌ Error al guardar el crédito.');
      }
    });
  }

  private limpiarFormulario() {
    this.clienteExiste = false;
    this.credito = {
      nombre_completo: '',
      cedula: '',
      telefono: '',
      direccion_residencia: '',
      capital_prestado: null,
      porcentaje_interes: 20,
      meses_duracion: 1,
      frecuencia_pago: 'diario'
    };
  }
}