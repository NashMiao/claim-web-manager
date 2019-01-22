let chesiccTableVisible = false;

let chesiccClaim = {
    name: '',
    gender: '',
    nationalID: '',
    nation: '',
    birthData: '',
    school: '',
    level: '',
    department: '',
    schClass: '',
    major: '',
    stuId: '',
    entryTime: '',
    schDuration: '',
    stuFrom: '',
    stuType: '',
    rollState: ''
};

let reloadPotPage = async function () {
    window.location.reload();
};

let getChesiccClaimInfo = async function () {
    // try{
    //     let url = Flask.url_for('chesicc_claim_info');
    // }catch (error) {
    //     console.log(error);
    // }
    url = "http://127.0.0.1:5001/chesicc_claim_info";
    try {
        let response = await axios.get(url);
        let info = response.data.result;
        this.chesiccClaim.name = info['姓名'];
        this.chesiccClaim.gender = info['性别'];
        this.chesiccClaim.nationalID = info['证件号码'];
        this.chesiccClaim.nation = info['民族'];
        this.chesiccClaim.birthData = info['出生日期'];
        this.chesiccClaim.school = info['院校'];
        this.chesiccClaim.level = info['层次'];
        this.chesiccClaim.department = info['院系'];
        this.chesiccClaim.schClass = info['班级'];
        this.chesiccClaim.major = info['专业'];
        this.chesiccClaim.stuId = info['学号'];
        this.chesiccClaim.entryTime = info['入学时间'];
        this.chesiccClaim.schDuration = info['学制'];
        this.chesiccClaim.stuFrom = info['形式'];
        this.chesiccClaim.stuType = info['类型'];
        this.chesiccClaim.rollState = info['学籍状态'];
    } catch (error) {
    }
};