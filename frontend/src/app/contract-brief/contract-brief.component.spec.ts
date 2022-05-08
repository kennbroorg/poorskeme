import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractBriefComponent } from './contract-brief.component';

describe('ContractBriefComponent', () => {
  let component: ContractBriefComponent;
  let fixture: ComponentFixture<ContractBriefComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ContractBriefComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ContractBriefComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
