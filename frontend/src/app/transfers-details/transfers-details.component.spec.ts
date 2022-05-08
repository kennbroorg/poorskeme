import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TransfersDetailsComponent } from './transfers-details.component';

describe('TransfersDetailsComponent', () => {
  let component: TransfersDetailsComponent;
  let fixture: ComponentFixture<TransfersDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TransfersDetailsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TransfersDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
