<template>
    <div>
        <div id="kakaoMap"></div>
    </div>
</template>

<script>
    export default {
        props: {
            locations: {
                type: Array,
                required: true,
            },
        },
        data () {
            return {
                map : null
            }
        },
        mounted() {
            try {
                const script = document.createElement("script");
                const key = process.env.VUE_APP_KAKAO_API_KEY
                
                script.src = `//dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${key}&libraries=clusterer`;
                document.head.appendChild(script);
                /*
                스크립트가 로드 되기전에 kakao객체에 접근하여 kakao객체를 찾지 못해 발생하는 에러를
                방지하기 위해 스크립트가 로드 된 뒤에 실제 지도를 그리도록 함
                */
                script.onload = () => { 
                    kakao.maps.load(() => {
                        var container = document.getElementById('kakaoMap'); // 지도를 담을 영역의 DOM 레퍼런스
                        var options = { // 지도를 생성할 때 필요한 기본 옵션
                            center: new kakao.maps.LatLng(36.0, 128.0), // 지도의 중심좌표
                            level: 15// 지도의 레벨(확대, 축소 정도)
                        };
                        // eslint-disable-next-line no-unused-vars
                        var map = new kakao.maps.Map(container, options); // 지도 생성 및 객체 리턴

                        // 클러스터러 생성
                        var clusterer = new kakao.maps.MarkerClusterer({
                            map: map, // 마커 클러스터러가 사용할 지도
                            averageCenter: true, // 클러스터 중심을 마커 중심으로
                            minLevel: 10 // 최소 클러스터링 레벨
                        });

                        // 마커 생성 및 클러스터러에 추가
                        var markers = this.locations.map(location => {
                            return new kakao.maps.Marker({
                                position: new kakao.maps.LatLng(
                                    parseFloat(location.latitude),
                                    parseFloat(location.longitude)
                                ),
                            });
                        });

                        clusterer.addMarkers(markers); // 클러스터러에 마커 추가
                    });
                };
            } catch (error) {
                alert("Maps :" + error.message);
            } finally {
                // 오류 여부와 관계없이 실행될 코드 (예: 로딩 스피너 숨기기 등)
                console.log("load KAKAOmap");
            }
        },
        methods() {}
    }
</script>

<style scoped>
    #kakaoMap {
        width: 100%; /* 적절한 너비로 설정 */
        height: 80vh; /* 뷰포트 높이의 80% */
        margin: 0px auto; /* 상단 여백은 17px, 좌우 가운데 정렬 */
        display: block; /* 가운데 정렬을 위해 블록 요소로 설정 */
        } 
</style>