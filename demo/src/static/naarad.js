var chartsList = [];
var timeseriesChartsList = [];
var cdfChartsList = [];
var timeseriesOptionsList = [];
var cdfOptionsList = [] ;
var chartIndex = 0;
var syncRange;
var colorSets = [
["#1F78B4", "#B2DF8A", "#A6CEE3"],
["#993399", "#B3CDE3", "#CCEBC5"],
null
];
var resourcesPrefix = "resources/";
var resourcesSuffix = ".csv";

function switchDiffTable(metric)
{
    display_choice = document.getElementById("radio-diff-" + metric).checked;
    if (display_choice) {
        document.getElementById("table-diff-percent-" + metric).hidden = false;
        document.getElementById("table-diff-absolute-" + metric).hidden = true;
    } else {
        document.getElementById("table-diff-percent-" + metric).hidden = true;
        document.getElementById("table-diff-absolute-" + metric).hidden = false;
    }
}

function plot(selector_id, reset_selector_id, div_id, colorset_id, advanced_source, url_div)
{
  document.getElementById(reset_selector_id).selectedIndex=0;
  var chartIndex = parseInt(selector_id.split("-")[2]);
  var chart_data_selector = document.getElementById(selector_id);
  var chart_data_source = "";
  var chart_data_title = "" ;
  chart_data_source = chart_data_selector.options[chart_data_selector.selectedIndex].value;
  chart_data_title = chart_data_selector.options[chart_data_selector.selectedIndex].text;
  document.getElementById(url_div).innerHTML = "<a href=" + chart_data_source + " target=\"_blank\">[csv]</a>"
  var div_width = document.getElementById(div_id).clientWidth;
  var div_height = document.getElementById(div_id).clientHeight;
  var blockRedraw = false;
  var initialized = false;
  chart_1 = new Dygraph(document.getElementById(div_id), chart_data_source,
  {
    axes : {
      x : {
            ticker: Dygraph.dateTicker
          },
      y : {
            drawGrid: true
          }
    },
    legend: 'always',
    xValueParser: function(x) {
       var date_components = x.split(/[^0-9]/);
       return new Date(date_components[0], date_components[1]-1, date_components[2], date_components[3], date_components[4], date_components[5], date_components[6] || 0).getTime();
    },
    xlabel: "Time",
    colors: colorSets[colorset_id],
    labels: [ "Time", chart_data_title],
    labelsDiv: "labels-" + div_id,
    dateWindow: syncRange,
    drawCallback: function(me, initial) {
      if (blockRedraw || initial) return;
      blockRedraw = true;
      syncRange = me.xAxisRange();
      for (var i = 0; i < timeseriesChartsList.length; i++)
      {
        if (timeseriesChartsList[i] == me) continue;
        if (timeseriesChartsList[i] != null)
        {
            timeseriesChartsList[i].updateOptions({
                dateWindow: syncRange
            });
        }
      }
    updateShareUrl();
    blockRedraw = false;
    }
  }
  );
  chart_1.resize(div_width, window.screen.height*0.75/2);
  chartsList[chartIndex] = chart_1;
  timeseriesChartsList[chartIndex] = chart_1;
  cdfChartsList[chartIndex] = null;
  updateShareUrl();
}

function plotCdf(selector_id, reset_selector_id, div_id, colorset_id, advanced_source, url_div)
{
  document.getElementById(reset_selector_id).selectedIndex=0;
  var chartIndex = parseInt(selector_id.split("-")[2]);
  var chart_data_selector = document.getElementById(selector_id);
  var chart_data_source = "";
  var chart_data_title = "" ;
  chart_data_source = chart_data_selector.options[chart_data_selector.selectedIndex].value;
  chart_data_title = chart_data_selector.options[chart_data_selector.selectedIndex].text;
  document.getElementById(url_div).innerHTML = "<a href=" + chart_data_source + " target=\"_blank\">[csv]</a>"
  var div_width = document.getElementById(div_id).clientWidth;
  var div_height = document.getElementById(div_id).clientHeight;
  chart_1 = new Dygraph(document.getElementById(div_id), chart_data_source,
  {
    axes : {
      y : {
            drawGrid: true
          }
    },
    legend: 'always',
    xlabel: "Percentiles",
    colors: colorSets[colorset_id],
    labels: [ "Percentiles", chart_data_title],
    labelsDiv: "labels-" + div_id
  }
  );
  chart_1.resize(div_width, window.screen.height*0.75/2);
  chartsList[chartIndex] = chart_1;
  cdfChartsList[chartIndex] = chart_1;
  timeseriesChartsList[chartIndex] = null;
  updateShareUrl();
}

function addChart(container_div)
{
  chartIndex++;

  var chartDiv = document.createElement("div");
  chartDiv.className = "content";
  chartDiv.setAttribute("id","chart-div-" + chartIndex.toString());

  var selectionDiv = document.createElement("div");
  selectionDiv.className = "row";
  selectionDiv.innerHTML = document.getElementById("selection-div-0").innerHTML.replace(/-0/g, "-" + chartIndex.toString());;
  chartDiv.appendChild(selectionDiv);

  var removeChartButton = document.createElement("button");
  removeChartButton.className = "btn btn-danger";
  removeChartButton.type = "button";
  var removeChartButtonText = document.createTextNode("-");
  removeChartButton.appendChild(removeChartButtonText);
  removeChartButton.setAttribute("onclick", "removeChart('chart-div-" + chartIndex.toString() + "'," + chartIndex.toString() + ")");

  var labelsChartingDiv = document.createElement("div");
  labelsChartingDiv.setAttribute("id","labels-charting-div-" + chartIndex.toString());
  chartDiv.appendChild(labelsChartingDiv);

  var chartingDiv = document.createElement("div");
  chartingDiv.className = "row";
  chartingDiv.style.height = "50%"
  chartingDiv.style.width = "100%"
  chartingDiv.setAttribute("id","charting-div-" + chartIndex.toString());
  chartDiv.appendChild(chartingDiv);

  var csvURLDiv = document.createElement("div");
  csvURLDiv.setAttribute("id","csv-url-div-" + chartIndex.toString());
  chartDiv.appendChild(csvURLDiv);

  document.getElementById(container_div).appendChild(chartDiv);
  document.getElementById("button-div-" + chartIndex.toString()).appendChild(removeChartButton);
}

function uploadFile()
{
    var formData = new FormData();
    var xhr = new XMLHttpRequest();
    for(var i = 0; i < document.getElementById("the-file").files.length; i++)
    {
        formData.append("file[]", document.getElementById("the-file").files[i]);
    }
    xhr.open("POST", "/analyze", true);
    xhr.send(formData);
    document.getElementById("the-file").value = "";
    document.getElementById("status-div").innerHTML = "Upload Complete. Request has been queued for analysis."
}

function removeChart(chart_div, index)
{
  var current_chart_div = document.getElementById(chart_div);
  current_chart_div.parentNode.removeChild(current_chart_div);
  timeseriesChartsList[index] = null;
  cdfChartsList[index] = null;
  chartsList[index] = null;
  updateShareUrl();
}

function updateShareUrl()
{
    document.getElementById("text-share-report-url").value = saveChartState();
}

function saveChartState()
{
  if (chartsList.length == 0)
  {
      return window.location.toString();
  }
  var chartState = window.location.toString().split("?")[0] + "?charts=";
  for(var i = 0; i < chartsList.length; i++)
  {
        if (chartsList[i] != null)
        {
           chartState += chartsList[i].file_ + "," ;
        }
  }
  chartState = chartState.replace(/,$/,"");
  chartState += "&range=" + syncRange ;
  return chartState;
}

function getOptions()
{
  for(var i = 0; i < document.getElementById('select-chart-0').options.length; i++)
  {
    timeseriesOptionsList[i] = document.getElementById('select-chart-0').options[i].label;
  }
  for(var i = 0; i < document.getElementById('select-percentiles-0').options.length; i++)
  {
    cdfOptionsList[i] = document.getElementById('select-percentiles-0').options[i].label;
  }
}

function loadSavedChart()
{
  var urlComponents = window.location.toString().split(/[?&]/);
  var charts = [];
  var range = [];
  getOptions();
  for(var i = 1; i < urlComponents.length; i++)
  {
    if(urlComponents[i].indexOf("charts=") >= 0 )
    {
      charts = urlComponents[i].split(/[=,]/);
    } else if(urlComponents[i].indexOf("range=") >= 0 )
    {
      range = urlComponents[i].split(/[=,]/);
      if (range.length == 3)
      {
        syncRange = [parseFloat(range[1]),parseFloat(range[2])];
      }
    }
  }
  for(var i = 1; i < charts.length; i++)
  {
    if(i > 1)
    {
      addChart('chart-parent-div');
    }
    if(charts[i].indexOf("percentiles.csv") > 0)
    {
        selectDropdown('select-percentiles-' + (i-1), charts[i]);
        plotCdf('select-percentiles-' + (i-1),'select-chart-' + (i-1),'charting-div-' + (i-1),0,false,'csv-url-div-' + (i-1));
    } else
    {
        selectDropdown('select-chart-' + (i-1), charts[i]);
        plot('select-chart-' + (i-1),'select-percentiles-' + (i-1),'charting-div-' + (i-1),0,false,'csv-url-div-' + (i-1));
    }
  }
  updateShareUrl();
}

function selectDropdown(dropdownId, dropdownValue)
{
  var dropdown = document.getElementById(dropdownId);
  for(var i = 0; i < dropdown.options.length; i++)
  {
    if(dropdown.options[i].value == dropdownValue)
    {
      dropdown.options[i].selected = true;
      return;
    }
  }
}

function filter(timeseriesSelector, cdfSelector, filterId)
{
  var filteredTimeseriesList = [];
  var filteredCDFList = [];
  var filters = [];
  var filterText = document.getElementById(filterId).value.trim().replace(/[ ]+/," ");
  if(filterText.length > 0)
  {
    filters = filterText.split(" ");
    filteredTimeseriesList = filterList(filters,timeseriesOptionsList);
    if (filteredTimeseriesList.length > 1)
    {
      purgeOptions(timeseriesSelector);
      addOptions(timeseriesSelector, filteredTimeseriesList);
    }
    filteredCDFList = filterList(filters,cdfOptionsList);
    if (filteredCDFList.length > 1)
    {
      purgeOptions(cdfSelector);
      addOptions(cdfSelector, filteredCDFList);
    }
  }
}

function filterList(filters, list)
{
  var filteredList = [];
  filteredList[0] = list[0];
  for(var i = 1; i < list.length; i++)
  {
    for(var j = 0; j < filters.length; j++)
    {
      if(list[i].indexOf(filters[j]) > -1)
      {
        filteredList.push(list[i]);
        continue;
      }
    }
  }
  return filteredList;
}

function getOptionElement(text)
{
  var option = document.createElement("option");
  option.text = text;
  option.value = resourcesPrefix + text + resourcesSuffix;
  return option
}


function purgeOptions(selectorId)
{
  var select = document.getElementById(selectorId);
  select.innerHTML = "";
}

function addOptions(selectorId, list)
{
  var select = document.getElementById(selectorId);
  for(var i = 0; i < list.length; i++)
  {
    select.add(getOptionElement(list[i]));
  }
}
