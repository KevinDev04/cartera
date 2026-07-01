import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ListaCobros } from './components/lista-cobros/lista-cobros';
import { NuevoCredito } from './components/nuevo-credito';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ListaCobros, NuevoCredito],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent {
  title = 'cobros-cartera-frontend';


//Variable para controlar si se ve o no el formulario
mostrarFormulario = false;

//Funcion para abrir y cerrar el formulario

alternarFormulario(){
  this.mostrarFormulario = !this.mostrarFormulario;
}
}