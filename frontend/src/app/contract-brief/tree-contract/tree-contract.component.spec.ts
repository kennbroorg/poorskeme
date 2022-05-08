import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TreeContractComponent } from './tree-contract.component';

describe('TreeContractComponent', () => {
  let component: TreeContractComponent;
  let fixture: ComponentFixture<TreeContractComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TreeContractComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TreeContractComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
