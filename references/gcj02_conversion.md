# WGS-84 → GCJ-02 坐标转换算法

在交互地图版 HTML 中，将此代码内嵌到 `<script>` 标签内。

## 算法代码

```javascript
var PI = Math.PI;
var A = 6378245.0;
var EE = 0.00669342162296594323;

function transformLat(x, y) {
  var ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x));
  ret += (20.0 * Math.sin(6.0 * x * PI) + 20.0 * Math.sin(2.0 * x * PI)) * 2.0 / 3.0;
  ret += (20.0 * Math.sin(y * PI) + 40.0 * Math.sin(y / 3.0 * PI)) * 2.0 / 3.0;
  ret += (160.0 * Math.sin(y / 12.0 * PI) + 320 * Math.sin(y * PI / 30.0)) * 2.0 / 3.0;
  return ret;
}

function transformLon(x, y) {
  var ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x));
  ret += (20.0 * Math.sin(6.0 * x * PI) + 20.0 * Math.sin(2.0 * x * PI)) * 2.0 / 3.0;
  ret += (20.0 * Math.sin(x * PI) + 40.0 * Math.sin(x / 3.0 * PI)) * 2.0 / 3.0;
  ret += (150.0 * Math.sin(x / 12.0 * PI) + 300.0 * Math.sin(x / 30.0 * PI)) * 2.0 / 3.0;
  return ret;
}

function outOfChina(lat, lng) {
  return (lng < 72.004 || lng > 137.8347) || (lat < 0.8293 || lat > 55.8271);
}

function wgs84ToGcj02(lat, lng) {
  if (outOfChina(lat, lng)) {
    return [lat, lng];
  }
  var dLat = transformLat(lng - 105.0, lat - 35.0);
  var dLon = transformLon(lng - 105.0, lat - 35.0);
  var radLat = lat / 180.0 * PI;
  var magic = Math.sin(radLat);
  magic = 1 - EE * magic * magic;
  var sqrtMagic = Math.sqrt(magic);
  dLat = (dLat * 180.0) / ((A * (1 - EE)) / (magic * sqrtMagic) * PI);
  dLon = (dLon * 180.0) / (A / sqrtMagic * Math.cos(radLat) * PI);
  return [lat + dLat, lng + dLon];
}
```

## 使用方式

```javascript
// 所有标记坐标先转换
var gcjPoints = routeData.stations.map(function(s) {
  var converted = wgs84ToGcj02(s.lat, s.lng);
  return { original: s, gcj: converted };
});

// 用转换后的坐标创建标记和折线
L.polyline(gcjPoints.map(p => p.gcj), { color: '#c0522a' }).addTo(map);
gcjPoints.forEach((p, i) => {
  L.marker(p.gcj, { icon: createNumberIcon(i + 1) }).addTo(map);
});
```

## 注意事项

- 此算法仅适用于中国大陆境内
- 高德地图、腾讯地图瓦片使用 GCJ-02
- OpenStreetMap、Google Map 使用 WGS-84，无需转换
- 海外城市直接使用原始坐标即可，跳过转换
