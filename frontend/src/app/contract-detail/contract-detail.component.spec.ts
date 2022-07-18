import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractDetailComponent } from './contract-detail.component';

describe('ContractDetailComponent', () => {
  let component: ContractDetailComponent;
  let fixture: ComponentFixture<ContractDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ContractDetailComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ContractDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
