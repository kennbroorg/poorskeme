import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TrxDetailsComponent } from './trx-details.component';

describe('TrxDetailsComponent', () => {
  let component: TrxDetailsComponent;
  let fixture: ComponentFixture<TrxDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TrxDetailsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TrxDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
