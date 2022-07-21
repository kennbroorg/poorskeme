import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NbThemeModule, NbLayoutModule, NbCardModule, NbTabsetModule } from '@nebular/theme';
import { NbButtonModule } from '@nebular/theme';
import { NbEvaIconsModule } from '@nebular/eva-icons';
import { NbDialogModule } from '@nebular/theme';

import { AppRoutingModule } from './app-routing.module';
import { HttpClientModule } from '@angular/common/http';
// import { NgxChartsModule } from '@swimlane/ngx-charts/ngx-charts.module';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { LineChartModule } from 'ngx-graph';
import { TreeNgxModule } from 'tree-ngx';

import { NgxDatatableModule } from '@swimlane/ngx-datatable';

import { HighlightModule, HIGHLIGHT_OPTIONS, HighlightOptions } from 'ngx-highlightjs';

// import { GojsAngularModule } from 'gojs-angular';
import { NgxOrgChartModule } from 'ngx-org-chart';

import { ContractResumeComponent } from './contract-resume/contract-resume.component';
import { ContractDetailComponent } from './contract-detail/contract-detail.component';
import { ContractCodeComponent } from './contract-code/contract-code.component';
import { DiagramComponent } from './contract-diagram/contract-diagram.component';

import { TransactionsBriefComponent } from './transactions-brief/transactions-brief.component';
import { TransfersBriefComponent } from './transfers-brief/transfers-brief.component';
import { ContractBriefComponent } from './contract-brief/contract-brief.component';
import { TransfersComponent } from './transfers/transfers.component';
import { LiqTransComponent } from './liq-trans/liq-trans.component';
import { TreeContractComponent } from './contract-brief/tree-contract/tree-contract.component';
import { TransfersDetailsComponent } from './transfers-details/transfers-details.component';

@NgModule({
  declarations: [
    AppComponent,
    TransactionsBriefComponent,
    TransfersBriefComponent,
    ContractBriefComponent,
    TransfersComponent,
    LiqTransComponent,
    TreeContractComponent,
    TransfersDetailsComponent,
    ContractResumeComponent,
    ContractDetailComponent,
    ContractCodeComponent,
    DiagramComponent,
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    NbThemeModule.forRoot({ name: 'dark' }),
    NbLayoutModule,
    NbEvaIconsModule,
    NbCardModule,
    NbTabsetModule,
    NbButtonModule,
    HttpClientModule,
    NgxChartsModule,
    LineChartModule,
    TreeNgxModule,
    NgxDatatableModule,
    HighlightModule,
    AppRoutingModule,
    // GojsAngularModule,
    NgxOrgChartModule,
    NbDialogModule.forChild()
  ],
  providers: [
    {
      provide: HIGHLIGHT_OPTIONS,
      useValue: <HighlightOptions>{
        lineNumbers: true,
        coreLibraryLoader: () => import('highlight.js/lib/core'),
        // lineNumbersLoader: () => import('highlightjs-line-numbers.js'),
        languages: {
          typescript: () => import('highlight.js/lib/languages/typescript'),
          css: () => import('highlight.js/lib/languages/css'),
          xml: () => import('highlight.js/lib/languages/xml'),
        },
      },
    },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
