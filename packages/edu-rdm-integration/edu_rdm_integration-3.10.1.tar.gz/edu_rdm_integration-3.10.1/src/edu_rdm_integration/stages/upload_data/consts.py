from edu_rdm_integration.stages.upload_data.models import (
    DataMartRequestStatus,
)


FAILED_STATUSES = {
    DataMartRequestStatus.FAILED_PROCESSING,
    DataMartRequestStatus.REQUEST_ID_NOT_FOUND,
    DataMartRequestStatus.FLC_ERROR,
}
