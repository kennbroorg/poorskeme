import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LiqTransComponent } from './liq-trans.component';

describe('LiqTransComponent', () => {
  let component: LiqTransComponent;
  let fixture: ComponentFixture<LiqTransComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LiqTransComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LiqTransComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
