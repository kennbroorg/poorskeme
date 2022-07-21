import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractCodeComponent } from './contract-code.component';

describe('ContractCodeComponent', () => {
  let component: ContractCodeComponent;
  let fixture: ComponentFixture<ContractCodeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ContractCodeComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ContractCodeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
