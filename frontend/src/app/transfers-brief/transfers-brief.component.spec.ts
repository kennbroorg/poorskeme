import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TransfersBriefComponent } from './transfers-brief.component';

describe('TransfersBriefComponent', () => {
  let component: TransfersBriefComponent;
  let fixture: ComponentFixture<TransfersBriefComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TransfersBriefComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TransfersBriefComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
