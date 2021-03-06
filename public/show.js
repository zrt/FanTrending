serverUrl = './'
wordlist = []

function showFanTrending(word){
	word = decodeURIComponent(word)
	console.log('show '+word)
	$.get(serverUrl + 'show?w='+word, function(data,status){
		datalist = JSON.parse(data)
		// console.log(datalist)
		var dom = document.getElementById("container");
		var myChart = echarts.init(dom);
		var app = {};
		option = null;
		var base = +new Date();
		var oneDay = 24 * 3600 * 1000;
		var data = [];
		var now = new Date(base);
		var mx = 0
		for(var i=1; i<=datalist.length;i++){
			var dayStr = [now.getFullYear(), now.getMonth() + 1, now.getDate()].join('-');
			data.push([dayStr, datalist[datalist.length-i]]);
			var now = new Date(base -= oneDay);
			mx =Math.max(datalist[datalist.length-i],mx)
		}
		
		option = {
		    animation: true,
		    title: {
		        left: 'left',
		        text: '关键词「'+word+'」 (max: '+mx+')',
		        subtext: '与"'+word+'"相关的饭否"七日年化"数量',
		    },
		    legend: {
		        top: 'bottom',
		        data:['trending']
		    },
		    tooltip: {
		        // triggerOn: 'none',
		        // position: function (pt) {
		        //     return [pt[0], 100];
		        // }
		    },
		    toolbox: {
		        left: 'right',
		        itemSize: 25,
		        top: 55,
		        feature: {
		            dataZoom: {
		                yAxisIndex: 'none'
		            },
		            restore: {}
		        }
		    },
		    xAxis: {
		        type: 'time',
		        // boundaryGap: [0, 0],
		        axisPointer: {
		            value: '2016-10-7',
		            snap: true,
		            lineStyle: {
		                color: '#004E52',
		                opacity: 0.5,
		                width: 2
		            },
		            label: {
		                show: true,
		                formatter: function (params) {
		                    return echarts.format.formatTime('yyyy-MM-dd', params.value);
		                },
		                backgroundColor: '#004E52'
		            },
		            handle: {
		                show: true,
		                color: '#004E52'
		            }
		        },
		        splitLine: {
		            show: false
		        }
		    },
		    yAxis: {
		        type: 'value',
		        axisTick: {
		            inside: true
		        },
		        splitLine: {
		            show: false
		        },
		        axisLabel: {
		            inside: true,
		            formatter: '{value}\n'
		        },
		        z: 10
		    },
		    grid: {
		        top: 110,
		        left: 15,
		        right: 15,
		        height: 160
		    },
		    dataZoom: [{
		        type: 'inside',
		        throttle: 50
		    }],
		    series: [
		        {
		            name: word,
		            type:'line',
		            smooth: true,
		            symbol: 'circle',
		            symbolSize: 5,
		            sampling: 'average',
		            itemStyle: {
		                normal: {
		                    color: '#8ec6ad'
		                }
		            },
		            stack: 'a',
		            areaStyle: {
		                normal: {
		                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
		                        offset: 0,
		                        color: '#8ec6ad'
		                    }, {
		                        offset: 1,
		                        color: '#ffe'
		                    }])
		                }
		            },
		            data: data
		        }

		    ]
		};
		if (option && typeof option === "object") {
		    myChart.setOption(option, true);
		}
	})

	
	
}

function selectFrom( number) {
    return Math.floor(Math.random() * number)
}
function addSel(){
	for(var i =0;i<wordlist.length;i++){
		$('<option value ="'+i+'">'+wordlist[i]+'</option>').appendTo('#sel')
	}
}

function selectChange(){
	var selectValue = $("#sel").val()
	console.log(selectValue)
	if (selectValue !== 'random'){
		var newUrl = changeURLArg(window.location.href,'w',wordlist[parseInt(selectValue)])
		var stateObject = {};
		var title = "change address"
		history.pushState(stateObject, title, newUrl);
		showFanTrending(wordlist[parseInt(selectValue)])
	}
}

function changeURLArg(url,arg,arg_val){
    var pattern=arg+'=([^&]*)';
    var replaceText=arg+'='+arg_val; 
    if(url.match(pattern)){
        var tmp='/('+ arg+'=)([^&]*)/gi';
        tmp=url.replace(eval(tmp),replaceText);
        return tmp;
    }else{ 
        if(url.match('[\?]')){ 
            return url+'&'+replaceText; 
        }else{ 
            return url+'?'+replaceText; 
        } 
    }
}

function getQueryString(key){
  var reg = new RegExp("(^|&)"+key+"=([^&]*)(&|$)");
  var result = window.location.search.substr(1).match(reg);
  return result?decodeURIComponent(result[2]):null;
}
$(function(){
	$.get(serverUrl + 'list', function(data,status){
		wordlist = JSON.parse(data)
		addSel(wordlist)
		$("#sel").change(function() { selectChange(); });
		var myw=getQueryString("w");
		if(myw !=null && myw.toString().length>1)
		{
			console.log('arg '+(myw))
		   showFanTrending((myw))
		}else showFanTrending(wordlist[selectFrom(wordlist.length)])
	})

});