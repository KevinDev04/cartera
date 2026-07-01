import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListaCobros } from './lista-cobros';

describe('ListaCobros', () => {
  let component: ListaCobros;
  let fixture: ComponentFixture<ListaCobros>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListaCobros],
    }).compileComponents();

    fixture = TestBed.createComponent(ListaCobros);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
