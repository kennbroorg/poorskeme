import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TransactionsBriefComponent } from './transactions-brief.component';

describe('TransactionsBriefComponent', () => {
  let component: TransactionsBriefComponent;
  let fixture: ComponentFixture<TransactionsBriefComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TransactionsBriefComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TransactionsBriefComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
