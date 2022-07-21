import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractResumeComponent } from './contract-resume.component';

describe('ContractBriefComponent', () => {
  let component: ContractResumeComponent;
  let fixture: ComponentFixture<ContractResumeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ContractResumeComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ContractResumeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
