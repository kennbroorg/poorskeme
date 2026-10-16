import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractCollectComponent } from './contract-collect.component';

describe('ContractBriefComponent', () => {
  let component: ContractCollectComponent;
  let fixture: ComponentFixture<ContractCollectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ContractCollectComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ContractCollectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
